import streamlit as st

# ページの設定
st.set_page_config(page_title="今日のおもちゃ", layout="wide")

# メインページ（ホーム）
st.markdown("<h1 style='text-align: center; margin-top: 10vh;'>今日のおもちゃ</h1>", unsafe_allow_html=True)
st.write("---")
st.write("サイドバーからおもちゃを選んで遊んでね！")
