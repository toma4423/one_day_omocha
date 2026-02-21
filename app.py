import streamlit as st
from src.utils.styles import render_donation_box

# ページの設定
st.set_page_config(page_title="今日のおもちゃ箱", layout="wide", page_icon="🎁")

# メインページ（ホーム）
st.markdown("<h1 style='text-align: center; margin-top: 2vh;'>🎁 今日のおもちゃ箱</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>サイドバーからおもちゃを選んで遊んでね！</p>", unsafe_allow_html=True)
st.write("---")

# 各おもちゃの説明エリア
st.subheader("📦 おもちゃの紹介")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🎲 ゲーム系
    - **サイコロ**: 最大100個のダイスを一度に振れるシンプルなツール。
    - **双六メーカー**: 自由にマス目を作って遊べるすごろく盤。
    - **黒ひげ危機一発**: ハラハラドキドキの定番パーティーゲーム。
    - **マインスイーパー**: 爆弾を避けて地雷原を切り拓くクラシックパズル。
    - **チンチロリン**: 本格的な役判定とアニメーション付きのサイコロ勝負。
    """)

with col2:
    st.markdown("""
    ### 🔢 サポート・ツール系
    - **カウントサポート**: X, Y, Z の3つの数値に倍率をかけて計算できるカウンタ。
    - **カウントサポートビンゴ**: 複数の項目をグリッド形式で同時にカウント。CSVでの保存・復元にも対応！
    """)

st.write("---")

# 開発支援エリアを最後に配置
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    PAYPAY_URL = "https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s"
    render_donation_box(PAYPAY_URL)
