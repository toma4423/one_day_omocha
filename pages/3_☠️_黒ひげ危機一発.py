import streamlit as st
import random
from src.utils.styles import render_donation_box

st.set_page_config(page_title="黒ひげ危機一発", page_icon="☠️")

# 募金箱設置
PAYPAY_URL = "https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s"
render_donation_box(PAYPAY_URL)

# セッション状態の初期化
if 'kurohige_status' not in st.session_state:
    st.session_state.kurohige_status = "ready"
if 'kurohige_target' not in st.session_state:
    st.session_state.kurohige_target = -1
if 'kurohige_clicked' not in st.session_state:
    st.session_state.kurohige_clicked = []

def reset_game(num_slots):
    st.session_state.kurohige_target = random.randint(0, num_slots - 1)
    st.session_state.kurohige_clicked = []
    st.session_state.kurohige_status = "playing"

st.title("☠️ 黒ひげ危機一発")

num_slots = st.sidebar.slider("穴の数", 4, 24, 12)

# ゲーム開始またはリセット
if st.session_state.kurohige_status == "ready" or st.sidebar.button("リセット"):
    reset_game(num_slots)
    st.rerun()

# 状態に応じたヘッダー表示
if st.session_state.kurohige_status == "boom":
    st.markdown("<h1 style='text-align:center; font-size:100px;'>🚀 🏴‍☠️</h1><h2 style='text-align:center; color:red;'>ドカン！！！</h2>", unsafe_allow_html=True)
    st.snow()
else:
    st.markdown("<h1 style='text-align:center; font-size:100px;'>🛢️</h1>", unsafe_allow_html=True)

# 穴（ボタン）の表示
cols_per_row = 4
for i in range(0, num_slots, cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx < num_slots:
            with col:
                # すでにクリックされたか、爆発済みの場合は無効化
                if idx in st.session_state.kurohige_clicked:
                    st.button("🗡️", key=f"k_{idx}", disabled=True, use_container_width=True)
                elif st.session_state.kurohige_status == "boom":
                    st.button("🕳️", key=f"k_{idx}", disabled=True, use_container_width=True)
                else:
                    if st.button("❓", key=f"k_{idx}", use_container_width=True):
                        if idx == st.session_state.kurohige_target:
                            st.session_state.kurohige_status = "boom"
                        else:
                            st.session_state.kurohige_clicked.append(idx)
                        st.rerun()
