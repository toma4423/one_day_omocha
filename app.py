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
    ### 🎲 ゲーム・エンタメ系
    - **サイコロ**: 最大100個を一度に！**出目履歴の自動保存**にも対応。
    - **双六メーカー**: 自由にマスを作れる。**自動コマ移動とループ機能**で本格プレイ。
    - **黒ひげ危機一発**: 番号表示で分かりやすい。**中断しても続きから**遊べます。
    - **マインスイーパー**: 定番の頭脳パズル。地雷の位置も自動で保持。
    - **チンチロリン**: アニメーションと役判定。**対戦履歴を自動記録**します。
    """)

with col2:
    st.markdown("""
    ### 🔢 サポート・ツール系
    - **カウントサポート**: X, Y, Z を倍率計算。**JSONでの保存・復元**が可能に。
    - **カウントサポートビンゴ**: 最大 15×15 の多機能カウンタ。**自動保存とJSON入出力**を完備。
    """)

st.info("💡 **すべてのツールは「自動保存」に対応しています。** ブラウザをリロードしたり閉じたりしても、あなたのデータは手元のデバイスに安全に保持されます。")

st.write("---")

# 開発支援エリアを最後に配置
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    PAYPAY_URL = "https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s"
    render_donation_box(PAYPAY_URL)
