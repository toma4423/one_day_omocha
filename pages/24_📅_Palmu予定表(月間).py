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
            if val == "スキップ":
                val = "SKIP"
            st.session_state[f"pm_day_{i}"] = val
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
st.markdown("1ヶ月間のランクポイント予定を管理し、配信用のスケジュール画像を作成します。")

# --- サイドバー：セーブ＆ロード ---
with st.sidebar:
    st.header("💾 セーブ & ロード")
    current_data = {f"day_{i}": st.session_state[f"pm_day_{i}"] for i in range(1, MAX_MONTH_DAYS + 1)}
    current_data["skip_cards"] = st.session_state.palmu_month_skip_cards
    json_str = json.dumps(current_data, indent=2)
    st.download_button(
        "📥 JSON保存",
        json_str,
        f"palmu_month_{get_jst_now().strftime('%Y%m%d')}.json",
        "application/json",
        use_container_width=True,
    )
    uploaded_file = st.file_uploader("📤 JSON読込", type="json")
    if uploaded_file and st.button("復元する", use_container_width=True):
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
    if st.button("🚨 全リセット", use_container_width=True):
        for i in range(1, MAX_MONTH_DAYS + 1):
            st.session_state[f"pm_day_{i}"] = 1
        st.session_state.palmu_month_skip_cards = 0
        st.session_state.palmu_month_reset_counter += 1
        storage.delete_item(PALMU_MONTH_STORAGE_KEY)
        st.rerun()

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
PERIOD_COLORS = ["#E0E0E0", "#E3F2FD", "#F1F8E9", "#FFF3E0", "#F3E5F5", "#EFEBE9"]
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
                    st.markdown(
                        f"<div style='background-color:{p_color}; border-radius:4px; font-size:10px; text-align:center; border:1px solid #ddd; margin-bottom:4px;'>第{p_idx if p_idx > 0 else '休'}期</div>",
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

# --- 画像生成 ---
st.write("---")
st.header("🗓️ 画像生成 & 合成")
with st.container(border=True):
    bg_file = st.file_uploader("🖼️ 背景アップロード", type=["jpg", "png"], key="pm_bg")
    cs1, cs2 = st.columns([1, 2])
    with cs1:
        title_text = st.text_input("タイトル", value=f"{start_date.month}月 スケジュール", key="pm_title")
        img_width = st.number_input("幅", 400, 1200, 800, 10, key="pm_width")
        img_text_color = st.color_picker("文字色", "#FFFFFF", key="pm_txt_c")
        img_frame_color = st.color_picker("枠色", "#FF5722", key="pm_frm_c")
    with cs2:
        is_trans = st.checkbox("透過", False, key="pm_trans")
        img_bg_rgba = (
            "#00000000"
            if is_trans
            else f"{st.color_picker('枠内色', '#000000', key='pm_bg_c')}{int(st.slider('不透明度', 0, 100, 80, key='pm_a') * 255 / 100):02X}"
        )

    if bg_file:
        cp, csc = st.columns(2)
        with cp:
            anchor = st.selectbox("基準点", ["左上", "中央", "右上", "左下", "右下"], key="pm_anchor")
            px = st.number_input("Xズレ", value=st.session_state.get("p_x", 0), key="p_x_in")
            py = st.number_input("Yズレ", value=st.session_state.get("p_y", 0), key="p_y_in")
            st.session_state.p_x, st.session_state.p_y = px, py
        with csc:
            scale = st.slider("スケール", 0.1, 2.0, 1.0, 0.05, key="pm_scale")
    else:
        anchor, px, py, scale = "左上", 0, 0, 1.0

    if st.button("画像を生成する", use_container_width=True, type="primary", key="pm_gen"):
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
        final_bytes = composite_images(bg_file.getvalue(), fg_bytes, px, py, scale, anchor) if bg_file else fg_bytes
        st.markdown(
            f'<div style="text-align:center; background:#eee; padding:20px; border-radius:16px;"><img src="data:image/png;base64,{base64.b64encode(final_bytes).decode()}" style="max-width:100%;"></div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            "📥 保存",
            final_bytes,
            f"palmu_month_{get_jst_now().strftime('%Y%m%d')}.png",
            "image/png",
            use_container_width=True,
        )

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
