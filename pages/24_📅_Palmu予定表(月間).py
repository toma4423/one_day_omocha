import base64
import json
from datetime import timedelta

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.image_maker import composite_images, create_palmu_calendar_grid_image
from src.utils.palmu import (
    calculate_skip_card_balance,
    evaluate_rank_status,
    get_day_period_assignments,
    group_points_by_active_week,
    points_needed_for_rank_up,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header
from src.utils.time import get_jst_now

st.set_page_config(page_title="Palmu月間予定表", page_icon="📅", layout="wide")

# グローバルスタイルの適用
render_page_header()

# ストレージ設定
storage = SafeStorage(LocalStorage())
PALMU_MONTH_STORAGE_KEY = "palmu_month_data"
MAX_MONTH_DAYS = 31

# セッション状態の初期化
if "palmu_month_reset_counter" not in st.session_state:
    st.session_state.palmu_month_reset_counter = 0
if "palmu_month_skip_cards" not in st.session_state:
    st.session_state.palmu_month_skip_cards = 0


def save_to_storage():
    data = {f"day_{i}": st.session_state.get(f"pm_day_{i}", 1) for i in range(1, MAX_MONTH_DAYS + 1)}
    data["skip_cards"] = st.session_state.get("palmu_month_skip_cards", 0)
    storage.set_item(PALMU_MONTH_STORAGE_KEY, data)


def load_from_storage():
    data = storage.get_item(PALMU_MONTH_STORAGE_KEY, is_json=True)
    if data:
        for i in range(1, MAX_MONTH_DAYS + 1):
            val = data.get(f"day_{i}", 1)
            st.session_state[f"pm_day_{i}"] = "SKIP" if val == "スキップ" else val
        st.session_state.palmu_month_skip_cards = data.get("skip_cards", 0)
        return True
    return False


def init_palmu_month_state():
    if "pm_day_1" not in st.session_state:
        if not load_from_storage():
            for i in range(1, MAX_MONTH_DAYS + 1):
                st.session_state[f"pm_day_{i}"] = 1
            st.session_state.palmu_month_skip_cards = 0


init_palmu_month_state()

st.title("📅 Palmu月間予定表マネージャー")

# --- 基本設定 ---
with st.container(border=True):
    st.subheader("📅 スケジュール設定")
    c1, c2, c3 = st.columns(3)
    with c1:
        start_date = st.date_input("開始日", value=get_jst_now().date())
    with c2:
        num_days = st.number_input("表示日数", 7, MAX_MONTH_DAYS, 31)
    with c3:
        st.session_state.palmu_month_skip_cards = st.number_input(
            "所持スキップカード数", 0, 10, value=st.session_state.palmu_month_skip_cards
        )

# --- 入力グリッド ---
point_options = ["SKIP", 1, 2, 4, 6]
# 視認性の高い配色
PERIOD_COLORS = [
    "#F5F5F5",  # 0: SKIP/休み (ライトグレー)
    "#BBDEFB",  # 1: 青
    "#C8E6C9",  # 2: 緑
    "#FFE0B2",  # 3: オレンジ
    "#E1BEE7",  # 4: 紫
    "#FFF9C4",  # 5: 黄色
]
weekdays_sun = ["日", "月", "火", "水", "木", "金", "土"]

st.subheader(f"📝 デイリーポイント入力 ({num_days}日間)")
daily_vals = [st.session_state.get(f"pm_day_{i}", 1) for i in range(1, num_days + 1)]
period_assigns = get_day_period_assignments(daily_vals)
skip_balances = calculate_skip_card_balance(st.session_state.palmu_month_skip_cards, start_date, num_days, daily_vals)

start_weekday_idx = (start_date.weekday() + 1) % 7
total_slots = num_days + start_weekday_idx
rows = (total_slots + 6) // 7
reset_id = st.session_state.palmu_month_reset_counter

# ヘッダー
cols_h = st.columns(7)
for i, dname in enumerate(weekdays_sun):
    color = "#FF1744" if dname == "日" else ("#2979FF" if dname == "土" else "inherit")
    cols_h[i].markdown(
        f"<div style='text-align:center; font-weight:bold; color:{color};'>{dname}</div>", unsafe_allow_html=True
    )

# グリッド
for r in range(rows):
    cols = st.columns(7)
    for c in range(7):
        slot_idx = r * 7 + c
        day_idx = slot_idx - start_weekday_idx + 1
        with cols[c]:
            if 1 <= day_idx <= num_days:
                curr_d = start_date + timedelta(days=day_idx - 1)
                p_idx = period_assigns[day_idx - 1]
                p_color = PERIOD_COLORS[p_idx % len(PERIOD_COLORS)]
                with st.container(border=True):
                    # 期バッジの視認性改善 (文字色を濃く、太字に)
                    st.markdown(
                        f"<div style='background-color:{p_color}; border-radius:4px; font-size:10px; text-align:center; border:1px solid #ccc; margin-bottom:4px; color:#333; font-weight:bold;'>第{p_idx if p_idx > 0 else '休'}期</div>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"🎫{skip_balances[day_idx - 1]} {curr_d.month}/{curr_d.day}")
                    st.session_state[f"pm_day_{day_idx}"] = st.selectbox(
                        "P",
                        point_options,
                        index=point_options.index(st.session_state[f"pm_day_{day_idx}"])
                        if st.session_state[f"pm_day_{day_idx}"] in point_options
                        else 1,
                        key=f"pm_p_{day_idx}_{reset_id}",
                        label_visibility="collapsed",
                        on_change=save_to_storage,
                        format_func=lambda x: f"+{x}" if isinstance(x, int) else str(x),
                    )

# --- 分析 ---
st.write("---")
st.header("📈 ランク状況分析")
active_weeks = group_points_by_active_week([st.session_state[f"pm_day_{i}"] for i in range(1, num_days + 1)])
if active_weeks:
    cols_w = st.columns(min(len(active_weeks), 4))
    for w, pts in enumerate(active_weeks):
        with cols_w[w % 4]:
            with st.container(border=True):
                total = sum(pts)
                status = evaluate_rank_status(total)
                st.markdown(f"**第 {w + 1} 期**")
                color = "#2E7D32" if status == "ランクアップ" else ("#E65100" if status == "キープ" else "#C62828")
                st.markdown(f"<h3 style='color:{color}; margin:0;'>{status}</h3>", unsafe_allow_html=True)
                st.metric("合計", f"{total} pt")
                if status != "ランクアップ":
                    st.caption(f"あと {points_needed_for_rank_up(total)}pt でアップ")

# --- 画像生成（ライブプレビュー） ---
st.write("---")
st.header("🗓️ 画像生成 & ライブプレビュー")
with st.container(border=True):
    bg_file = st.file_uploader("🖼️ 背景アップロード", type=["jpg", "png"], key="pm_bg")
    col_cfg, col_prev = st.columns([1, 1.5])

    with col_cfg:
        with st.expander("🎨 デザイン詳細設定", expanded=True):
            title_text = st.text_input("タイトル", value=f"{start_date.month}月 スケジュール", key="pm_title")
            c1, c2 = st.columns(2)
            with c1:
                img_text_color = st.color_picker("文字色", "#FFFFFF", key="pm_txt_c")
            with c2:
                img_frame_color = st.color_picker("枠色", "#FF5722", key="pm_frm_c")

            img_width = st.number_input("幅", 400, 1200, 800, 10, key="pm_width")

            is_trans = st.checkbox("枠内を完全に透過する", False, key="pm_trans")
            if not is_trans:
                c1, c2 = st.columns([1, 2])
                with c1:
                    img_bg_base = st.color_picker("枠内色", "#000000", key="pm_bg_c")
                with c2:
                    img_bg_alpha = st.slider("不透明度", 0, 100, 80, key="pm_a")
                img_bg_rgba = f"{img_bg_base}{int(img_bg_alpha * 255 / 100):02X}"
            else:
                img_bg_rgba = "#00000000"

        if bg_file:
            with st.expander("📍 配置設定", expanded=True):
                anchor = st.selectbox(
                    "基準点", ["左上", "中央", "右上", "左下", "右下", "中央左", "中央右", "中央上", "中央下"], key="pm_anchor"
                )
                c1, c2 = st.columns(2)
                with c1:
                    px = st.slider(
                        "X軸調整", -1000, 1000, value=st.session_state.get("p_x", 0), step=5, key="p_x_slider"
                    )
                with c2:
                    py = st.slider(
                        "Y軸調整", -1000, 1000, value=st.session_state.get("p_y", 0), step=5, key="p_y_slider"
                    )

                st.session_state.p_x, st.session_state.p_y = px, py
                scale = st.slider(
                    "スケール", 0.1, 2.0, value=st.session_state.get("p_scale", 1.0), step=0.05, key="pm_scale_slider"
                )
                st.session_state.p_scale = scale

            if st.button("🖱️ マウスで直感的に配置する (試験的機能)", key="pm_visual_btn"):
                st.session_state.pm_show_visual_editor = not st.session_state.get("pm_show_visual_editor", False)
        else:
            anchor, px, py, scale = "左上", 0, 0, 1.0

    with col_prev:
        st.subheader("🖼️ プレビュー")
        try:
            cal_data = [{"date": "", "day": weekdays_sun[i], "point": ""} for i in range(start_weekday_idx)]
            for i in range(1, num_days + 1):
                curr_d = start_date + timedelta(days=i - 1)
                p = st.session_state[f"pm_day_{i}"]
                cal_data.append(
                    {
                        "date": str(curr_d.day),
                        "day": weekdays_sun[(start_weekday_idx + i - 1) % 7],
                        "point": "SKIP" if p == "SKIP" else f"+{p}pt",
                    }
                )

            fg_bytes = create_palmu_calendar_grid_image(
                title_text, cal_data, img_text_color, img_frame_color, img_bg_rgba, img_width
            )

            from io import BytesIO

            from PIL import Image

            fg_img_size = Image.open(BytesIO(fg_bytes)).size
            fg_w, fg_h = fg_img_size

            if bg_file:
                final_bytes = composite_images(bg_file.getvalue(), fg_bytes, px, py, scale, anchor)
            else:
                final_bytes = fg_bytes

            st.markdown(
                f'<div style="text-align:center; background:#eee; padding:10px; border-radius:12px; border:1px solid #ddd;"><img src="data:image/png;base64,{base64.b64encode(final_bytes).decode()}" style="max-width:100%; height:auto;"></div>',
                unsafe_allow_html=True,
            )

            if st.session_state.get("pm_show_visual_editor", False) and bg_file:
                import streamlit.components.v1 as components

                bg_b64 = base64.b64encode(bg_file.getvalue()).decode()
                fg_b64 = base64.b64encode(fg_bytes).decode()

                editor_html = f"""
                <div id="wrapper" style="position: relative; border: 1px solid #ccc; display: inline-block; background: #f0f0f0; max-width: 100%;">
                    <canvas id="canvas"></canvas>
                </div>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
                <script>
                    const canvas = new fabric.Canvas('canvas');
                    const MAX_DISPLAY_WIDTH = 800;
                    
                    fabric.Image.fromURL('data:image/png;base64,{bg_b64}', function(bgImg) {{
                        const displayScale = Math.min(1.0, MAX_DISPLAY_WIDTH / bgImg.width);
                        const displayWidth = bgImg.width * displayScale;
                        const displayHeight = bgImg.height * displayScale;

                        canvas.setWidth(displayWidth);
                        canvas.setHeight(displayHeight);
                        
                        bgImg.scale(displayScale);
                        canvas.setBackgroundImage(bgImg, canvas.renderAll.bind(canvas));
                        
                        fabric.Image.fromURL('data:image/png;base64,{fg_b64}', function(fgImg) {{
                            let origLeft = {px};
                            let origTop = {py};
                            const fgOrigW = {fg_w} * {scale};
                            const fgOrigH = {fg_h} * {scale};

                            if ("{anchor}" === "中央") {{
                                origLeft = (bgImg.width - fgOrigW) / 2 + {px};
                                origTop = (bgImg.height - fgOrigH) / 2 + {py};
                            }} else if ("{anchor}" === "右上") {{
                                origLeft = (bgImg.width - fgOrigW) - {px};
                                origTop = {py};
                            }} else if ("{anchor}" === "左下") {{
                                origLeft = {px};
                                origTop = (bgImg.height - fgOrigH) - {py};
                            }} else if ("{anchor}" === "右下") {{
                                origLeft = (bgImg.width - fgOrigW) - {px};
                                origTop = (bgImg.height - fgOrigH) - {py};
                            }} else if ("{anchor}" === "中央左") {{
                                origLeft = {px};
                                origTop = (bgImg.height - fgOrigH) / 2 + {py};
                            }} else if ("{anchor}" === "中央右") {{
                                origLeft = (bgImg.width - fgOrigW) - {px};
                                origTop = (bgImg.height - fgOrigH) / 2 + {py};
                            }} else if ("{anchor}" === "中央上") {{
                                origLeft = (bgImg.width - fgOrigW) / 2 + {px};
                                origTop = {py};
                            }} else if ("{anchor}" === "中央下") {{
                                origLeft = (bgImg.width - fgOrigW) / 2 + {px};
                                origTop = (bgImg.height - fgOrigH) - {py};
                            }}

                            fgImg.set({{
                                left: origLeft * displayScale,
                                top: origTop * displayScale,
                                scaleX: {scale} * displayScale,
                                scaleY: {scale} * displayScale,
                                selectable: true,
                                hasControls: true,
                                cornerColor: 'rgba(0,0,255,0.5)',
                                cornerSize: 12,
                                transparentCorners: false
                            }});
                            canvas.add(fgImg);
                            canvas.setActiveObject(fgImg);
                        }});
                    }});
                </script>
                <p style="font-size: 0.8em; color: #666; margin-top: 10px;">
                    ※ 表示は画面サイズに合わせて縮小されていますが、相対的な位置関係は維持されています。
                </p>
                """
                st.info("💡 巨大な画像も画面内に収まるように自動調整されています。")
                components.html(editor_html, height=800, scrolling=True)

            st.write("")
            st.download_button(
                "📥 完成した画像を保存",
                final_bytes,
                f"palmu_month_{get_jst_now().strftime('%Y%m%d')}.png",
                "image/png",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"プレビュー生成エラー: {e}")

# --- データの保存と読み込み ---
st.write("---")
with st.container(border=True):
    st.subheader("📁 データの保存と読み込み")
    c1, c2 = st.columns(2)
    with c1:
        current_data = {f"day_{i}": st.session_state[f"pm_day_{i}"] for i in range(1, MAX_MONTH_DAYS + 1)}
        current_data["skip_cards"] = st.session_state.palmu_month_skip_cards
        json_str = json.dumps(current_data, indent=2, ensure_ascii=False)
        st.download_button(
            "📥 JSONを保存",
            json_str,
            f"palmu_month_{get_jst_now().strftime('%Y%m%d')}.json",
            "application/json",
            use_container_width=True,
        )
    with c2:
        uploaded_file = st.file_uploader("📤 JSONを読み込む", type="json", label_visibility="collapsed")
        if uploaded_file and st.button("反映実行", use_container_width=True):
            try:
                d = json.load(uploaded_file)
                for i in range(1, MAX_MONTH_DAYS + 1):
                    v = d.get(f"day_{i}", 1)
                    st.session_state[f"pm_day_{i}"] = "SKIP" if v == "スキップ" else v
                st.session_state.palmu_month_skip_cards = d.get("skip_cards", 0)
                save_to_storage()
                st.rerun()
            except Exception:
                st.error("読込失敗")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    if st.button("🚨 全リセット", use_container_width=True):
        for i in range(1, MAX_MONTH_DAYS + 1):
            st.session_state[f"pm_day_{i}"] = 1
        st.session_state.palmu_month_skip_cards = 0
        st.session_state.palmu_month_reset_counter += 1
        storage.delete_item(PALMU_MONTH_STORAGE_KEY)
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
