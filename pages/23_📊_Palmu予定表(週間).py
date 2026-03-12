import base64
import json
from datetime import timedelta

import streamlit as st
import streamlit.components.v1 as components
from streamlit_local_storage import LocalStorage

from src.utils.image_maker import composite_images, create_palmu_schedule_image
from src.utils.palmu import (
    calculate_skip_card_balance,
    calculate_total_points,
    calculate_weekly_display_days,
    evaluate_rank_status,
    generate_point_presets,
    generate_visual_editor_html,
    points_needed_for_keep,
    points_needed_for_rank_up,
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
BG_CACHE_KEY = "palmu_bg_cache_weekly"
MAX_TOTAL_DAYS = 21

# セッション状態の初期化
if "palmu_reset_counter" not in st.session_state:
    st.session_state.palmu_reset_counter = 0
if "palmu_skip_cards" not in st.session_state:
    st.session_state.palmu_skip_cards = 0


def save_to_storage():
    data = {f"day_{i}": st.session_state.get(f"palmu_day_{i}", 1) for i in range(1, MAX_TOTAL_DAYS + 1)}
    for i in range(1, MAX_TOTAL_DAYS + 1):
        data[f"plan_{i}"] = st.session_state.get(f"palmu_plan_{i}", "")
    data["skip_cards"] = st.session_state.get("palmu_skip_cards", 0)
    storage.set_item(PALMU_STORAGE_KEY, data)


def load_from_storage():
    data = storage.get_item(PALMU_STORAGE_KEY, is_json=True)
    if data:
        for i in range(1, MAX_TOTAL_DAYS + 1):
            val = data.get(f"day_{i}", 1)
            st.session_state[f"palmu_day_{i}"] = "SKIP" if val == "スキップ" else val
            st.session_state[f"palmu_plan_{i}"] = data.get(f"plan_{i}", "")
        st.session_state.palmu_skip_cards = data.get("skip_cards", 0)
        return True
    return False


def init_palmu_state():
    if "palmu_day_1" not in st.session_state:
        if not load_from_storage():
            for i in range(1, MAX_TOTAL_DAYS + 1):
                st.session_state[f"palmu_day_{i}"] = 1
                st.session_state[f"palmu_plan_{i}"] = ""
            st.session_state.palmu_skip_cards = 0
    # スライダーの初期化
    if "w_x_slider" not in st.session_state:
        st.session_state.w_x_slider = 0
    if "w_y_slider" not in st.session_state:
        st.session_state.w_y_slider = 0
    if "w_scale_slider" not in st.session_state:
        st.session_state.w_scale_slider = 1.0


init_palmu_state()

# --- ストレージによる同期 (座標とスケール) ---
sync_data = storage.get_item("palmu_sync_data", is_json=True)
if sync_data and sync_data.get("mode") == "weekly":
    st.session_state.w_x_slider = max(-1000, min(1000, int(sync_data.get("x", 0))))
    st.session_state.w_y_slider = max(-1000, min(1000, int(sync_data.get("y", 0))))
    st.session_state.w_scale_slider = max(0.1, min(2.0, float(sync_data.get("s", 1.0))))
    storage.delete_item("palmu_sync_data")
    st.rerun()

# --- 画像データの復元 ---
if "weekly_bg_cache" not in st.session_state:
    cached_bg_b64 = storage.get_item(BG_CACHE_KEY)
    if cached_bg_b64:
        try:
            st.session_state.weekly_bg_cache = base64.b64decode(cached_bg_b64)
        except Exception:
            st.session_state.weekly_bg_cache = None
    else:
        st.session_state.weekly_bg_cache = None

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
                    for i in range(1, MAX_TOTAL_DAYS + 1):
                        st.session_state[f"palmu_day_{i}"] = 1
                    for i, val in enumerate(p, 1):
                        st.session_state[f"palmu_day_{i}"] = val
                    save_to_storage()
                    st.rerun()

# --- 入力エリアの動的制御 ---
daily_vals = [st.session_state.get(f"palmu_day_{i}", 1) for i in range(1, MAX_TOTAL_DAYS + 1)]
display_days = calculate_weekly_display_days(daily_vals, MAX_TOTAL_DAYS)
skip_balances = calculate_skip_card_balance(st.session_state.palmu_skip_cards, start_date, MAX_TOTAL_DAYS, daily_vals)

point_options = ["SKIP", 1, 2, 4, 6]

col_input, col_result = st.columns([1.5, 1])
with col_input:
    st.subheader(f"📝 ポイント・予定入力 ({display_days}日間)")
    reset_id = st.session_state.palmu_reset_counter

    def on_point_change(idx):
        key = f"p_day_widget_{idx}_{reset_id}"
        st.session_state[f"palmu_day_{idx}"] = st.session_state[key]
        save_to_storage()

    for i in range(1, display_days + 1):
        curr_d = start_date + timedelta(days=i - 1)
        val = st.session_state[f"palmu_day_{i}"]
        is_skip = val == "SKIP"
        bg_color = "#F5F5F5" if is_skip else "#E3F2FD"

        with st.container(border=True):
            c_sel, c_plan, c_info = st.columns([2, 3, 1])
            with c_info:
                st.markdown(
                    f"<div style='background-color:{bg_color}; border-radius:8px; padding:4px; text-align:center; font-size:12px; border:1px solid #ddd; color:#333; font-weight:bold;'>{'休み' if is_skip else '配信'}</div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"🎫 {skip_balances[i - 1]}枚")
            with c_sel:
                st.selectbox(
                    f"{curr_d.strftime('%m/%d')} ({['月', '火', '水', '木', '金', '土', '日'][curr_d.weekday()]})",
                    options=point_options,
                    index=point_options.index(val) if val in point_options else 1,
                    key=f"p_day_widget_{i}_{reset_id}",
                    on_change=on_point_change,
                    args=(i,),
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
    st.subheader("📈 ランク状況分析")
    active_points = [
        st.session_state[f"palmu_day_{i}"]
        for i in range(1, display_days + 1)
        if st.session_state[f"palmu_day_{i}"] != "SKIP"
    ]
    total = calculate_total_points(active_points[:7])
    status = evaluate_rank_status(total)

    with st.container(border=True):
        st.markdown("**今期の最終判定予定**")
        colors = {
            "ランクアップ": ("#E8F5E9", "#2E7D32"),
            "キープ": ("#FFF3E0", "#E65100"),
            "ランクダウン": ("#FFEBEE", "#C62828"),
        }
        bg, fg = colors.get(status, ("#F5F5F5", "#333333"))
        render_result_box("判定結果", status, bg_color=bg, border_color=fg, text_color=fg, font_size=32)

        st.metric("有効7日間の合計", f"{total} pt")
        if status != "ランクアップ":
            if status == "ランクダウン":
                st.info(f"🛡️ キープまで: あと **{points_needed_for_keep(total)}** pt")
            st.success(f"🚀 ランクアップまで: あと **{points_needed_for_rank_up(total)}** pt")
        else:
            st.success("🎉 目標達成予定です！")


@st.dialog("📏 配置を直感的に調整する", width="large")
def show_palmu_editor(bg_bytes, fg_bytes, fg_w, fg_h, px, py, scale, anchor):
    st.markdown("#### 📱 ビジュアルエディタ")
    st.caption("画像をドラッグして移動、角を引いてサイズ変更できます。")
    html_content = generate_visual_editor_html(bg_bytes, fg_bytes, fg_w, fg_h, px, py, scale, anchor, mode="weekly")
    components.html(html_content, height=550, scrolling=True)


# --- 画像生成（ライブプレビュー） ---
st.write("---")
st.header("🗓️ 画像生成 & ライブプレビュー")
with st.container(border=True):
    bg_file = st.file_uploader("🖼️ 背景画像をアップロード", type=["jpg", "png"], key="weekly_bg")

    if bg_file:
        img_data = bg_file.getvalue()
        st.session_state.weekly_bg_cache = img_data
        storage.set_item(BG_CACHE_KEY, base64.b64encode(img_data).decode())

    active_bg = st.session_state.get("weekly_bg_cache")

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

            fg_bytes = create_palmu_schedule_image(
                title_text, sched_data, img_text_color, img_frame_color, img_bg_rgba, img_f_width, img_radius, img_width
            )
            from io import BytesIO

            from PIL import Image

            fg_img_size = Image.open(BytesIO(fg_bytes)).size
            fg_w, fg_h = fg_img_size

            if active_bg:
                with st.expander("📍 配置設定", expanded=True):
                    # --- 追加: 位置リセットボタンをスライダーより先に配置 ---
                    if st.button("🔄 位置とスケールをリセット", use_container_width=True):
                        st.session_state.w_x_slider = 0
                        st.session_state.w_y_slider = 0
                        st.session_state.w_scale_slider = 1.0
                        st.rerun()

                    anchor = st.selectbox(
                        "基準点", ["左上", "中央", "右上", "左下", "右下", "中央左", "中央右", "中央上", "中央下"]
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        px = st.slider("X軸調整", -1000, 1000, step=5, key="w_x_slider")
                    with c2:
                        py = st.slider("Y軸調整", -1000, 1000, step=5, key="w_y_slider")

                    scale = st.slider("スケール", 0.1, 2.0, step=0.05, key="w_scale_slider")

                if st.button("🖱️ マウスで直感的に配置する (試験的機能)", use_container_width=True):
                    show_palmu_editor(active_bg, fg_bytes, fg_w, fg_h, px, py, scale, anchor)

                if st.button("🖼️ 背景画像をクリア", use_container_width=True):
                    st.session_state.weekly_bg_cache = None
                    storage.delete_item(BG_CACHE_KEY)
                    st.rerun()
            else:
                anchor, px, py, scale = "左上", 0, 0, 1.0

        with col_preview_area:
            st.subheader("🖼️ プレビュー")
            final_bytes = composite_images(active_bg, fg_bytes, px, py, scale, anchor) if active_bg else fg_bytes

            st.markdown(
                f'<div style="text-align:center; background:#eee; padding:10px; border-radius:12px; border:1px solid #ddd;"><img src="data:image/png;base64,{base64.b64encode(final_bytes).decode()}" style="max-width:100%; height:auto;"></div>',
                unsafe_allow_html=True,
            )

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
        current_data = {f"day_{i}": st.session_state[f"palmu_day_{i}"] for i in range(1, MAX_TOTAL_DAYS + 1)}
        for i in range(1, MAX_TOTAL_DAYS + 1):
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
                for i in range(1, MAX_TOTAL_DAYS + 1):
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
        for i in range(1, MAX_TOTAL_DAYS + 1):
            st.session_state[f"palmu_day_{i}"] = 1
            st.session_state[f"palmu_plan_{i}"] = ""
        st.session_state.palmu_skip_cards = 0
        st.session_state.palmu_reset_counter += 1
        st.session_state.w_x_slider = 0
        st.session_state.w_y_slider = 0
        st.session_state.w_scale_slider = 1.0
        storage.delete_item(PALMU_STORAGE_KEY)
        storage.delete_item(BG_CACHE_KEY)
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
