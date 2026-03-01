import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.image_maker import create_palmu_schedule_image
from src.utils.palmu import (
    calculate_skip_card_balance,
    calculate_total_points,
    evaluate_rank_status,
    points_needed_for_keep,
    points_needed_for_rank_up,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header
from src.utils.time import get_jst_now

st.set_page_config(page_title="Palmu予定表(週間)", page_icon="📊", layout="wide")

# グローバルスタイルの適用
render_page_header()

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "pw_start_date" not in st.session_state:
    st.session_state.pw_start_date = get_jst_now().date()
if "pw_initial_cards" not in st.session_state:
    st.session_state.pw_initial_cards = 0
if "pw_daily_points" not in st.session_state:
    st.session_state.pw_daily_points = [1] * 7

st.title("📊 Palmu 週間予定表マネージャー")

# --- 設定セクション ---
with st.container(border=True):
    col_date, col_card = st.columns(2)
    with col_date:
        st.session_state.pw_start_date = st.date_input("開始日", st.session_state.pw_start_date)
    with col_card:
        st.session_state.pw_initial_cards = st.number_input(
            "初期スキップカード枚数", 0, 10, st.session_state.pw_initial_cards
        )

# --- 予定入力セクション ---
st.subheader("📝 配信予定の入力")
with st.container(border=True):
    point_options = ["SKIP", 0, 1, 2, 4, 6]
    cols = st.columns(7)
    for i in range(7):
        curr_date = st.session_state.pw_start_date + __import__("datetime").timedelta(days=i)
        with cols[i]:
            st.markdown(
                f"**{curr_date.strftime('%m/%d')}**\n({['月', '火', '水', '木', '金', '土', '日'][curr_date.weekday()]})"
            )
            st.session_state.pw_daily_points[i] = st.selectbox(
                f"P{i}",
                point_options,
                index=point_options.index(st.session_state.pw_daily_points[i]),
                key=f"pw_p_{i}",
                label_visibility="collapsed",
            )

# --- 計算・解析 ---
total_pts = calculate_total_points(st.session_state.pw_daily_points)
rank_status = evaluate_rank_status(total_pts)
skip_balances = calculate_skip_card_balance(
    st.session_state.pw_initial_cards, st.session_state.pw_start_date, 7, st.session_state.pw_daily_points
)

st.write("")
col_res1, col_res2 = st.columns(2)
with col_res1:
    with st.container(border=True):
        st.metric("合計ポイント", f"{total_pts} pt")
        st.subheader(f"判定: {rank_status}")
        if rank_status != "ランクアップ":
            st.write(f"ランクアップまであと **{points_needed_for_rank_up(total_pts)} pt**")
        if rank_status == "ランクダウン":
            st.write(f"キープまであと **{points_needed_for_keep(total_pts)} pt**")

with col_res2:
    with st.container(border=True):
        st.subheader("🃏 スキップカード推移")
        bal_str = " → ".join([str(b) for b in skip_balances])
        st.markdown(f"**{bal_str}**")
        st.caption("※月曜に+2枚(上限10)、SKIP日に-1枚で計算")

# --- 画像生成 ---
st.write("")
st.subheader("🖼️ 画像として保存")
with st.container(border=True):
    if st.button("予定表画像を生成する", use_container_width=True, type="primary"):
        sched_data = []
        for i in range(7):
            curr_date = st.session_state.pw_start_date + __import__("datetime").timedelta(days=i)
            p = st.session_state.pw_daily_points[i]
            val_str = "SKIP" if p == "SKIP" else f"+{p}pt"
            sched_data.append((curr_date.strftime("%m/%d"), val_str))

        img_bytes = create_palmu_schedule_image("WEEKLY SCHEDULE", sched_data)
        st.image(img_bytes, use_container_width=True)
        st.download_button(
            "画像を保存",
            img_bytes,
            file_name=f"palmu_week_{get_jst_now().strftime('%Y%m%d')}.png",
            mime="image/png",
            use_container_width=True,
        )

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
