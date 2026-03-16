import base64
from datetime import timedelta

import streamlit as st
import streamlit.components.v1 as components
from streamlit_local_storage import LocalStorage

from src.utils.image_maker import composite_images, create_palmu_calendar_grid_image
from src.utils.palmu import (
    calculate_monthly_display_days,
    calculate_skip_card_balance,
    evaluate_rank_status,
    generate_visual_editor_html,
    get_day_period_assignments,
    group_points_by_active_week,
    points_needed_for_rank_up,
)
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_storage_controls,
    wait_for_storage_load,
)
from src.utils.time import get_jst_now

st.set_page_config(page_title="Palmu月間予定表", page_icon="📅", layout="wide")

# グローバルスタイルの適用
render_page_header()

# ストレージ設定
storage = SafeStorage(LocalStorage())
PALMU_MONTH_STORAGE_KEY = "palmu_month_data"
BG_CACHE_KEY_MONTHLY = "palmu_bg_cache_monthly"
MAX_TOTAL_MONTH_DAYS = 60

# --- 初期化とロード (堅牢な方式) ---
if "pm_day_1" not in st.session_state:
    # 1. メインデータのロード待ち
    saved_data = wait_for_storage_load(storage, PALMU_MONTH_STORAGE_KEY, "_palmu_month_initialized")

    # 2. データの反映
    try:
        if saved_data:
            for i in range(1, MAX_TOTAL_MONTH_DAYS + 1):
                val = saved_data.get(f"day_{i}", 1)
                st.session_state[f"pm_day_{i}"] = "SKIP" if val == "スキップ" else val
            st.session_state.palmu_month_skip_cards = saved_data.get("skip_cards", 0)
        else:
            for i in range(1, MAX_TOTAL_MONTH_DAYS + 1):
                st.session_state[f"pm_day_{i}"] = 1
            st.session_state.palmu_month_skip_cards = 0
    except Exception:
        for i in range(1, MAX_TOTAL_MONTH_DAYS + 1):
            st.session_state[f"pm_day_{i}"] = 1
        st.session_state.palmu_month_skip_cards = 0

    # 3. その他非永続状態の初期化
    st.session_state.palmu_month_reset_counter = 0
    st.session_state.p_x_slider = 0
    st.session_state.p_y_slider = 0
    st.session_state.pm_scale_slider = 1.0

    st.rerun()

# --- ストレージによる同期 (座標とスケール) ---
sync_data = storage.get_item("palmu_sync_data", is_json=True)
if sync_data and sync_data.get("mode") == "monthly":
    st.session_state.p_x_slider = max(-1000, min(1000, int(sync_data.get("x", 0))))
    st.session_state.p_y_slider = max(-1000, min(1000, int(sync_data.get("y", 0))))
    st.session_state.pm_scale_slider = max(0.1, min(2.0, float(sync_data.get("s", 1.0))))
    storage.delete_item("palmu_sync_data")
    st.rerun()

# --- 画像データの復元 (リロード対策) ---
if "monthly_bg_cache" not in st.session_state:
    cached_bg_b64 = storage.get_item(BG_CACHE_KEY_MONTHLY)
    if cached_bg_b64:
        try:
            st.session_state.monthly_bg_cache = base64.b64decode(cached_bg_b64)
        except Exception:
            st.session_state.monthly_bg_cache = None
    else:
        st.session_state.monthly_bg_cache = None

st.title("📅 Palmu月間予定表マネージャー")

# --- 基本設定 ---
with st.container(border=True):
    st.subheader("📅 スケジュール設定")
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("開始日", value=get_jst_now().date())
    with c2:
        st.session_state.palmu_month_skip_cards = st.number_input(
            "所持スキップカード数", 0, 10, value=st.session_state.palmu_month_skip_cards
        )

# --- 動的な表示日数の計算 ---
daily_vals_all = [st.session_state.get(f"pm_day_{i}", 1) for i in range(1, MAX_TOTAL_MONTH_DAYS + 1)]
num_days = calculate_monthly_display_days(daily_vals_all, max_total=MAX_TOTAL_MONTH_DAYS)

# --- 入力グリッド ---
point_options = ["SKIP", 1, 2, 4, 6]
PERIOD_COLORS = ["#F5F5F5", "#BBDEFB", "#C8E6C9", "#FFE0B2", "#E1BEE7", "#FFF9C4"]
weekdays_sun = ["日", "月", "火", "水", "木", "金", "土"]

st.subheader(f"📝 デイリーポイント入力 ({num_days}日間)")
daily_vals = [st.session_state.get(f"pm_day_{i}", 1) for i in range(1, num_days + 1)]
period_assigns = get_day_period_assignments(daily_vals)
skip_balances = calculate_skip_card_balance(st.session_state.palmu_month_skip_cards, start_date, num_days, daily_vals)

start_weekday_idx = (start_date.weekday() + 1) % 7
total_slots = num_days + start_weekday_idx
rows = (total_slots + 6) // 7
reset_id = st.session_state.palmu_month_reset_counter


def on_pm_point_change(idx):
    key = f"pm_p_widget_{idx}_{reset_id}"
    st.session_state[f"pm_day_{idx}"] = st.session_state[key]


cols_h = st.columns(7)
for i, dname in enumerate(weekdays_sun):
    color = "#FF1744" if dname == "日" else ("#2979FF" if dname == "土" else "inherit")
    cols_h[i].markdown(
        f"<div style='text-align:center; font-weight:bold; color:{color};'>{dname}</div>", unsafe_allow_html=True
    )

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
                val = st.session_state.get(f"pm_day_{day_idx}", 1)
                with st.container(border=True):
                    st.markdown(
                        f"<div style='background-color:{p_color}; border-radius:4px; font-size:10px; text-align:center; border:1px solid #ccc; margin-bottom:4px; color:#333; font-weight:bold;'>第{p_idx if p_idx > 0 else '休'}期</div>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"🎫{skip_balances[day_idx - 1]} {curr_d.month}/{curr_d.day}")
                    st.selectbox(
                        "P",
                        point_options,
                        index=point_options.index(val) if val in point_options else 1,
                        key=f"pm_p_widget_{day_idx}_{reset_id}",
                        label_visibility="collapsed",
                        on_change=on_pm_point_change,
                        args=(day_idx,),
                        format_func=lambda x: f"+{x}" if isinstance(x, int) else str(x),
                    )

# --- 分析 ---
st.write("---")
st.header("📈 ランク状況分析")
active_weeks = group_points_by_active_week([st.session_state.get(f"pm_day_{i}", 1) for i in range(1, num_days + 1)])
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


@st.dialog("📏 配置を直感的に調整する", width="large")
def show_palmu_editor(bg_bytes, fg_bytes, fg_w, fg_h, px, py, scale, anchor):
    st.markdown("#### 📱 ビジュアルエディタ")
    st.caption("画像をドラッグして移動、角を引いてサイズ変更できます。")
    html_content = generate_visual_editor_html(bg_bytes, fg_bytes, fg_w, fg_h, px, py, scale, anchor, mode="monthly")
    components.html(html_content, height=550, scrolling=True)


# --- 画像生成 ---
st.write("---")
st.header("🗓️ 画像生成 & ライブプレビュー")
with st.container(border=True):
    bg_file = st.file_uploader("🖼️ 背景アップロード", type=["jpg", "png"], key="pm_bg")

    if bg_file:
        img_data = bg_file.getvalue()
        st.session_state.monthly_bg_cache = img_data
        storage.set_item(BG_CACHE_KEY_MONTHLY, base64.b64encode(img_data).decode())

    active_bg = st.session_state.get("monthly_bg_cache")

    try:
        cal_data = [{"date": "", "day": weekdays_sun[i], "point": ""} for i in range(start_weekday_idx)]
        for i in range(1, num_days + 1):
            curr_d = start_date + timedelta(days=i - 1)
            p = st.session_state.get(f"pm_day_{i}", 1)
            cal_data.append(
                {
                    "date": str(curr_d.day),
                    "day": weekdays_sun[(start_weekday_idx + i - 1) % 7],
                    "point": "SKIP" if p == "SKIP" else f"+{p}pt",
                }
            )

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

            fg_bytes = create_palmu_calendar_grid_image(
                title_text, cal_data, img_text_color, img_frame_color, img_bg_rgba, img_width
            )
            from io import BytesIO

            from PIL import Image

            fg_img_size = Image.open(BytesIO(fg_bytes)).size
            fg_w, fg_h = fg_img_size

            if active_bg:
                with st.expander("📍 配置設定", expanded=True):
                    # --- 追加: 位置リセットボタンをスライダーより先に配置 ---
                    if st.button("🔄 位置とスケールをリセット", use_container_width=True):
                        st.session_state.p_x_slider = 0
                        st.session_state.p_y_slider = 0
                        st.session_state.pm_scale_slider = 1.0
                        st.rerun()

                    anchor = st.selectbox(
                        "基準点",
                        ["左上", "中央", "右上", "左下", "右下", "中央左", "中央右", "中央上", "中央下"],
                        key="pm_anchor",
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        px = st.slider("X軸調整", -1000, 1000, step=5, key="p_x_slider")
                    with c2:
                        py = st.slider("Y軸調整", -1000, 1000, step=5, key="p_y_slider")

                    scale = st.slider("スケール", 0.1, 2.0, step=0.05, key="pm_scale_slider")

                if st.button("🖱️ マウスで直感的に配置する (試験的機能)", key="pm_visual_btn", use_container_width=True):
                    show_palmu_editor(active_bg, fg_bytes, fg_w, fg_h, px, py, scale, anchor)

                if st.button("🖼️ 背景画像をクリア", key="pm_clear_btn", use_container_width=True):
                    st.session_state.monthly_bg_cache = None
                    storage.delete_item(BG_CACHE_KEY_MONTHLY)
                    st.rerun()
            else:
                anchor, px, py, scale = "左上", 0, 0, 1.0

        with col_prev:
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
                f"palmu_month_{get_jst_now().strftime('%Y%m%d')}.png",
                "image/png",
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"プレビュー生成エラー: {e}")


# --- データの保存と読み込み ---
def on_load_pm(data: dict):
    for i in range(1, MAX_TOTAL_MONTH_DAYS + 1):
        v = data.get(f"day_{i}", 1)
        st.session_state[f"pm_day_{i}"] = "SKIP" if v == "スキップ" else v
    st.session_state.palmu_month_skip_cards = data.get("skip_cards", 0)


current_pm_data = {f"day_{i}": st.session_state.get(f"pm_day_{i}", 1) for i in range(1, MAX_TOTAL_MONTH_DAYS + 1)}
current_pm_data["skip_cards"] = st.session_state.palmu_month_skip_cards

render_storage_controls(
    storage=storage,
    storage_key=PALMU_MONTH_STORAGE_KEY,
    current_data=current_pm_data,
    on_load_callback=on_load_pm,
    file_prefix="palmu_month",
)

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    if st.button("🚨 全リセット", use_container_width=True):
        for i in range(1, MAX_TOTAL_MONTH_DAYS + 1):
            st.session_state[f"pm_day_{i}"] = 1
        st.session_state.palmu_month_skip_cards = 0
        st.session_state.pm_show_visual_editor = False
        st.session_state.monthly_bg_cache = None
        st.session_state.p_x_slider = 0
        st.session_state.p_y_slider = 0
        st.session_state.pm_scale_slider = 1.0
        storage.delete_item(PALMU_MONTH_STORAGE_KEY)
        storage.delete_item(BG_CACHE_KEY_MONTHLY)
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
