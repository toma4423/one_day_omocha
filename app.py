import streamlit as st
from src.utils.styles import render_donation_box

# ページの設定
st.set_page_config(page_title="今日のおもちゃ", layout="wide")

# サイドバーに募金箱を設置
PAYPAY_URL = "https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s"
render_donation_box(PAYPAY_URL)

# メインページ（ホーム）
st.markdown("<h1 style='text-align: center; margin-top: 10vh;'>今日のおもちゃ</h1>", unsafe_allow_html=True)
st.write("---")
st.write("サイドバーからおもちゃを選んで遊んでね！")
