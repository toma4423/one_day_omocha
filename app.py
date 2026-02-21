import streamlit as st
from src.utils.styles import render_donation_box

# ページの設定
st.set_page_config(page_title="今日のおもちゃ", layout="wide")

# メインページ（ホーム）
st.markdown("<h1 style='text-align: center; margin-top: 5vh;'>今日のおもちゃ</h1>", unsafe_allow_html=True)
st.write("---")

# 開発支援エリアをメインに配置
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    PAYPAY_URL = "https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s"
    render_donation_box(PAYPAY_URL)

st.write("---")
st.write("サイドバーからおもちゃを選んで遊んでね！")
