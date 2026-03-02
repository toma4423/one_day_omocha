import base64
import json
from datetime import timedelta

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.image_maker import composite_images, create_palmu_schedule_image
from src.utils.palmu import (
    calculate_skip_card_balance,
    calculate_total_points,
    evaluate_rank_status,
    generate_point_presets,
    get_day_period_assignments,
    points_needed_for_keep,
    points_needed_for_rank_up,
    render_visual_editor,
)
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_result_box,
)
from src.utils.time import get_jst_now

st.set_page_config(page_title="Palmu週間予定表", page_icon="📊", layout="wide")

# グローバルスタイルの適用
render_page_header()

# ストレージ設定
storage = SafeStorage(LocalStorage())
PALMU_STORAGE_KEY = "palmu_data"
MAX_DAYS = 14

# セッション状態の初期化
if "palmu_reset_counter" not in st.session_state:
    st.session_state.palmu_reset_counter = 0
if "palmu_skip_cards" not in st.session_state:
    st.session_state.palmu_skip_cards = 0


def save_to_storage():
    data = {f"day_{i}": st.session_state.get(f"palmu_day_{i}", 1) for i in range(1, MAX_DAYS + 1)}
    for i in range(1, MAX_DAYS + 1):
        data[f"plan_{i}"] = st.session_state.get(f"palmu_plan_{i}", "")
    data["skip_cards"] = st.session_state.get("palmu_skip_cards", 0)
    storage.set_item(PALMU_STORAGE_KEY, data)


def load_from_storage():
    data = storage.get_item(PALMU_STORAGE_KEY, is_json=True)
    if data:
        for i in range(1, MAX_DAYS + 1):
            val = data.get(f"day_{i}", 1)
            st.session_state[f"palmu_day_{i}"] = "SKIP" if val == "スキップ" else val
            st.session_state[f"palmu_plan_{i}"] = data.get(f"plan_{i}", "")
        st.session_state.palmu_skip_cards = data.get("skip_cards", 0)
        return True
    return False


def init_palmu_state():
    if "palmu_day_1" not in st.session_state:
        if not load_from_storage():
            for i in range(1, MAX_DAYS + 1):
                st.session_state[f"palmu_day_{i}"] = 1
                st.session_state[f"palmu_plan_{i}"] = ""
            st.session_state.palmu_skip_cards = 0


init_palmu_state()

# --- クエリパラメータによる同期 ---
if st.query_params.get("palmu_sync") == "1":
    try:
        # スライダーに反映させるためにsession_stateを更新
        st.session_state.w_x = int(st.query_params.get("palmu_x", 0))
        st.session_state.w_y = int(st.query_params.get("palmu_y", 0))
        st.session_state.w_scale = float(st.query_params.get("palmu_s", 1.0))
        # クリアしてリラン
        st.query_params.clear()
        st.rerun()
    except (ValueError, TypeError):
        pass

st.title("📊 Palmu週間予定表 (ランクメーター)")

# --- 基本設定 ---
with st.container(border=True):
    st.subheader("📅 スケジュール基本設定")
    col_date, col_target, col_skip = st.columns(3)
    with col_date:
        start_date = st.date_input("開始日", value=get_jst_now().date())
    with col_target:
        target_goal = st.selectbox("目標", options=["ランクアップ (+18pt)", "ランクキープ (+12pt)"])
        target_val = 18 if "アップ" in target_goal else 12
    with col_skip:
        st.session_state.palmu_skip_cards = st.number_input(
            "現在のスキップカード所持数", 0, 10, value=st.session_state.palmu_skip_cards, on_change=save_to_storage
        )

# --- おすすめプリセット ---
with st.expander("💡 おすすめのポイント取得パターンを見る"):
    st.markdown("目標達成のための効率的な構成例です。適用すると入力欄に反映されます。")
    presets = generate_point_presets(target_val)
    cols_preset = st.columns(len(presets))
    for idx, (p, col) in enumerate(zip(presets, cols_preset, strict=False)):
        with col:
            with st.container(border=True):
                st.markdown(f"**案 {idx + 1}**")
                st.markdown(f"**{sum(p)} pt**")
                p_str = "/".join([str(x) for x in p])
                st.caption(f"[{p_str}]")
                if st.button("適用", key=f"apply_{target_val}_{idx}", use_container_width=True):
                    for i in range(1, MAX_DAYS + 1):
                        st.session_state[f"palmu_day_{i}"] = p[i - 1] if i <= 7 else 1
                    save_to_storage()
                    st.rerun()

# --- 入力と計算 ---
point_options = ["SKIP", 1, 2, 4, 6]
PERIOD_COLORS = ["#E0E0E0", "#E3F2FD", "#F1F8E9", "#FFF3E0"]
daily_vals = [st.session_state.get(f"palmu_day_{i}", 1) for i in range(1, MAX_DAYS + 1)]
skip_balances = calculate_skip_card_balance(st.session_state.palmu_skip_cards, start_date, MAX_DAYS, daily_vals)
period_assigns = get_day_period_assignments(daily_vals)
active_period1 = [i for i, p in enumerate(period_assigns) if p == 1]
display_days = active_period1[-1] + 1 if active_period1 else 7

col_input, col_result = st.columns([1.5, 1])
with col_input:
    st.subheader(f"📝 ポイント・予定入力 ({display_days}日間)")
    reset_id = st.session_state.palmu_reset_counter
    for i in range(1, display_days + 1):
        curr_d = start_date + timedelta(days=i - 1)
        p_idx = period_assigns[i - 1]
        p_color = PERIOD_COLORS[p_idx % len(PERIOD_COLORS)]

        with st.container(border=True):
            c_sel, c_plan, c_info = st.columns([2, 3, 1])
            with c_info:
                st.markdown(
                    f"<div style='background-color:{p_color}; border-radius:8px; padding:4px; text-align:center; font-size:12px; border:1px solid #ddd;'>第{p_idx if p_idx > 0 else '休'}期</div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"🎫 {skip_balances[i - 1]}枚")
            with c_sel:
                st.session_state[f"palmu_day_{i}"] = st.selectbox(
                    f"{curr_d.strftime('%m/%d')} ({['月', '火', '水', '木', '金', '土', '日'][curr_d.weekday()]})",
                    options=point_options,
                    index=point_options.index(st.session_state[f"palmu_day_{i}"])
                    if st.session_state[f"palmu_day_{i}"] in point_options
                    else 1,
                    key=f"p_day_{i}_{reset_id}",
                    on_change=save_to_storage,
                    format_func=lambda x: f"+{x} pt" if isinstance(x, int) else str(x),
                )
            with c_plan:
                st.session_state[f"palmu_plan_{i}"] = st.text_input(
                    "予定テキスト",
                    value=st.session_state.get(f"palmu_plan_{i}", ""),
                    key=f"p_plan_{i}_{reset_id}",
                    on_change=save_to_storage,
                    placeholder="配信内容など",
                )

with col_result:
    st.subheader("📈 第1期の解析結果")
    p1_points = [st.session_state[f"palmu_day_{i + 1}"] for i, p in enumerate(period_assigns) if p == 1]
    total = calculate_total_points(p1_points)
    status = evaluate_rank_status(total)

    colors = {
        "ランクアップ": ("#E8F5E9", "#2E7D32"),
        "キープ": ("#FFF3E0", "#E65100"),
        "ランクダウン": ("#FFEBEE", "#C62828"),
    }
    bg, fg = colors.get(status, ("#F5F5F5", "#333333"))

    render_result_box("現在の判定", status, bg_color=bg, border_color=fg, text_color=fg, font_size=40)

    with st.container(border=True):
        st.metric("有効7日間の合計", f"{total} pt")
        if status != "ランクアップ":
            st.write("---")
            if status == "ランクダウン":
                st.info(f"🛡️ キープまで: あと **{points_needed_for_keep(total)}** pt")
            st.success(f"🚀 ランクアップまで: あと **{points_needed_for_rank_up(total)}** pt")
        else:
            st.success("🎉 目標達成予定です！")


@st.dialog("📏 配置を直感的に調整する", width="large")
def show_palmu_editor(bg_bytes, fg_bytes, fg_w, fg_h, px, py, scale, anchor):
    render_visual_editor(bg_bytes, fg_bytes, fg_w, fg_h, px, py, scale, anchor, mode="weekly")


# --- 画像生成（ライブプレビュー） ---
st.write("---")
st.header("🗓️ 画像生成 & ライブプレビュー")
with st.container(border=True):
    bg_file = st.file_uploader("🖼️ 背景画像をアップロード", type=["jpg", "png"], key="weekly_bg")

    col_style_cfg, col_preview_area = st.columns([1, 1.5])

    with col_style_cfg:
        with st.expander("🎨 デザイン詳細設定", expanded=True):
            title_text = st.text_input("タイトル", value=f"{start_date.month}/{start_date.day}〜 予定")
            c1, c2 = st.columns(2)
            with c1:
                img_text_color = st.color_picker("文字色", "#FFFFFF")
            with c2:
                img_frame_color = st.color_picker("枠色", "#FF5722")

            img_width = st.number_input("幅", 300, 1000, 600, 10)

            is_trans = st.checkbox("枠内を完全に透過する", False)
            if not is_trans:
                c1, c2 = st.columns([1, 2])
                with c1:
                    img_bg_base = st.color_picker("枠内色", "#000000")
                with c2:
                    img_bg_alpha = st.slider("不透明度", 0, 100, 80)
                img_bg_rgba = f"{img_bg_base}{int(img_bg_alpha * 255 / 100):02X}"
            else:
                img_bg_rgba = "#00000000"

            img_f_width = st.slider("枠の太さ", 0, 30, 8)
            img_radius = st.slider("角丸", 0, 200, 30)

        if bg_file:
            with st.expander("📍 配置設定", expanded=True):
                anchor = st.selectbox(
                    "基準点", ["左上", "中央", "右上", "左下", "右下", "中央左", "中央右", "中央上", "中央下"]
                )
                c1, c2 = st.columns(2)
                with c1:
                    # スライダーで直感的に調整できるように変更
                    px = st.slider(
                        "X軸調整", -1000, 1000, value=st.session_state.get("w_x", 0), step=5, key="w_x_slider"
                    )
                with c2:
                    py = st.slider(
                        "Y軸調整", -1000, 1000, value=st.session_state.get("w_y", 0), step=5, key="w_y_slider"
                    )

                st.session_state.w_x, st.session_state.w_y = px, py
                scale = st.slider(
                    "スケール", 0.1, 2.0, value=st.session_state.get("w_scale", 1.0), step=0.05, key="w_scale_slider"
                )
                st.session_state.w_scale = scale

            if st.button("🖱️ マウスで直感的に配置する (試験的機能)"):
                st.session_state.show_visual_editor = True
        else:
            anchor, px, py, scale = "左上", 0, 0, 1.0

    with col_preview_area:
        st.subheader("🖼️ プレビュー")
        try:
            sched_data = []
            for i in range(1, display_days + 1):
                curr_d = start_date + timedelta(days=i - 1)
                p = st.session_state[f"palmu_day_{i}"]
                plan = st.session_state.get(f"palmu_plan_{i}", "")
                sched_data.append(
                    (
                        f"{curr_d.month}/{curr_d.day} ({['月', '火', '水', '木', '金', '土', '日'][curr_d.weekday()]})",
                        plan,
                        "SKIP" if p == "SKIP" else f"+{p}pt",
                    )
                )

            fg_bytes = create_palmu_schedule_image(
                title_text, sched_data, img_text_color, img_frame_color, img_bg_rgba, img_f_width, img_radius, img_width
            )

            from io import BytesIO

            from PIL import Image

            fg_img_size = Image.open(BytesIO(fg_bytes)).size
            fg_w, fg_h = fg_img_size

            final_bytes = composite_images(bg_file.getvalue(), fg_bytes, px, py, scale, anchor) if bg_file else fg_bytes

            st.markdown(
                f'<div style="text-align:center; background:#eee; padding:10px; border-radius:12px; border:1px solid #ddd;"><img src="data:image/png;base64,{base64.b64encode(final_bytes).decode()}" style="max-width:100%; height:auto;"></div>',
                unsafe_allow_html=True,
            )

            if st.session_state.get("show_visual_editor", False) and bg_file:
                show_palmu_editor(bg_file.getvalue(), fg_bytes, fg_w, fg_h, px, py, scale, anchor)
                st.session_state.show_visual_editor = False

            st.write("")
            st.download_button(
                "📥 完成した画像を保存",
                final_bytes,
                f"palmu_week_{get_jst_now().strftime('%Y%m%d')}.png",
                "image/png",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"プレビュー生成中にエラーが発生しました: {e}")

# --- データの保存と読み込み ---
st.write("---")
with st.container(border=True):
    st.subheader("📁 データの保存と読み込み")
    c1, c2 = st.columns(2)
    with c1:
        current_data = {f"day_{i}": st.session_state[f"palmu_day_{i}"] for i in range(1, MAX_DAYS + 1)}
        for i in range(1, MAX_DAYS + 1):
            current_data[f"plan_{i}"] = st.session_state[f"palmu_plan_{i}"]
        current_data["skip_cards"] = st.session_state.palmu_skip_cards
        json_str = json.dumps(current_data, indent=2, ensure_ascii=False)
        st.download_button(
            "📥 JSONを保存",
            json_str,
            f"palmu_week_{get_jst_now().strftime('%Y%m%d')}.json",
            "application/json",
            use_container_width=True,
        )
    with c2:
        uploaded_file = st.file_uploader("📤 JSONを読み込む", type="json", label_visibility="collapsed")
        if uploaded_file and st.button("反映実行", use_container_width=True):
            try:
                d = json.load(uploaded_file)
                for i in range(1, MAX_DAYS + 1):
                    v = d.get(f"day_{i}", 1)
                    st.session_state[f"palmu_day_{i}"] = "SKIP" if v == "スキップ" else v
                    st.session_state[f"palmu_plan_{i}"] = d.get(f"plan_{i}", "")
                st.session_state.palmu_skip_cards = d.get("skip_cards", 0)
                save_to_storage()
                st.rerun()
            except Exception:
                st.error("読込失敗")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    if st.button("🚨 全入力をリセット", use_container_width=True):
        for i in range(1, MAX_DAYS + 1):
            st.session_state[f"palmu_day_{i}"] = 1
            st.session_state[f"palmu_plan_{i}"] = ""
        st.session_state.palmu_skip_cards = 0
        st.session_state.palmu_reset_counter += 1
        storage.delete_item(PALMU_STORAGE_KEY)
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
