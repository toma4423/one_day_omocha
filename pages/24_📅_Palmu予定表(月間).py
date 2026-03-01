import calendar
from datetime import date

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.image_maker import create_palmu_calendar_grid_image
from src.utils.palmu import (
    evaluate_rank_status,
    get_day_period_assignments,
    group_points_by_active_week,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header
from src.utils.time import get_jst_now

st.set_page_config(page_title="Palmu予定表(月間)", page_icon="📅", layout="wide")

# グローバルスタイルの適用
render_page_header()

# SafeStorage
storage = SafeStorage(LocalStorage())

# セッション初期化
if "pm_year" not in st.session_state:
    st.session_state.pm_year = get_jst_now().year
if "pm_month" not in st.session_state:
    st.session_state.pm_month = get_jst_now().month
if "pm_initial_cards" not in st.session_state:
    st.session_state.pm_initial_cards = 0

st.title("📅 Palmu 月間予定表マネージャー")

# --- 設定 ---
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.pm_year = st.number_input("年", 2024, 2100, st.session_state.pm_year)
    with c2:
        st.session_state.pm_month = st.number_input("月", 1, 12, st.session_state.pm_month)
    with c3:
        st.session_state.pm_initial_cards = st.number_input("初期カード数", 0, 10, st.session_state.pm_initial_cards)

num_days = calendar.monthrange(st.session_state.pm_year, st.session_state.pm_month)[1]
start_date = date(st.session_state.pm_year, st.session_state.pm_month, 1)

# 予定入力
st.subheader("📝 月間スケジュールの入力")
point_options = ["SKIP", 0, 1, 2, 4, 6]
daily_values = []

with st.container(border=True):
    for i in range(1, num_days + 1):
        d = date(st.session_state.pm_year, st.session_state.pm_month, i)
        w_name = ["月", "火", "水", "木", "金", "土", "日"][d.weekday()]
        col_d, col_p = st.columns([1, 3])
        with col_d:
            st.write(f"**{i}日 ({w_name})**")
        with col_p:
            val = st.selectbox(f"P{i}", point_options, index=2, key=f"pm_p_{i}", label_visibility="collapsed")
            daily_values.append(val)

# 解析
weeks = group_points_by_active_week(daily_values)
period_assigns = get_day_period_assignments(daily_values)

st.write("")
st.subheader("📊 ランク判定予測（期別）")
with st.container(border=True):
    cols_w = st.columns(len(weeks) if weeks else 1)
    for i, week_pts in enumerate(weeks):
        with cols_w[i]:
            total = sum(week_pts)
            st.metric(f"第 {i + 1} 期", f"{total} pt")
            st.caption(evaluate_rank_status(total))

# 画像生成
st.write("")
st.subheader("🖼️ カレンダー画像を生成")
with st.container(border=True):
    if st.button("月間カレンダーを生成", use_container_width=True, type="primary"):
        calendar_data = []
        cell_colors = []
        for i in range(1, num_days + 1):
            d = date(st.session_state.pm_year, st.session_state.pm_month, i)
            val = daily_values[i - 1]
            p_text = "SKIP" if val == "SKIP" else f"+{val}pt"
            calendar_data.append(
                {"date": str(i), "day": ["月", "火", "水", "木", "金", "土", "日"][d.weekday()], "point": p_text}
            )

            # 期ごとに色分け
            p_idx = period_assigns[i - 1]
            colors = ["#FFFFFF", "#E3F2FD", "#F1F8E9", "#FFF3E0", "#F3E5F5", "#EFEBE9"]
            cell_colors.append(colors[p_idx % len(colors)] if p_idx > 0 else "#EEEEEE")

        img_bytes = create_palmu_calendar_grid_image(
            f"{st.session_state.pm_month}月 SCHEDULE", calendar_data, cell_bg_colors=cell_colors
        )
        st.image(img_bytes, use_container_width=True)
        st.download_button(
            "画像を保存",
            img_bytes,
            file_name=f"palmu_month_{st.session_state.pm_month}.png",
            mime="image/png",
            use_container_width=True,
        )

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
