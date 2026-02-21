import streamlit as st
from src.utils.dice import roll_dice
from src.utils.styles import render_result_box, render_donation_box

st.set_page_config(page_title="サイコロ", page_icon="🎲")

# 募金箱設置
PAYPAY_URL = "https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s"
render_donation_box(PAYPAY_URL)

st.title("🎲 サイコロ")
col1, col2 = st.columns(2)
with col1: x = st.number_input("ダイスの数 (x)", 1, 100, 1)
with col2: n = st.number_input("ダイスの目の数 (n)", 1, 1000, 6)

if st.button("サイコロを振る！", use_container_width=True):
    results = roll_dice(x, n)
    total = sum(results)
    st.write("---")
    render_result_box("結果", total)
    st.balloons()
