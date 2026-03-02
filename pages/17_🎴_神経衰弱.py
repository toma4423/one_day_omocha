import streamlit as st

from src.utils.concentration import GameState, create_deck, handle_card_click
from src.utils.styles import render_donation_box, render_page_header, render_result_box

st.set_page_config(page_title="神経衰弱", page_icon="🎴", layout="wide")

# グローバルスタイルの適用
render_page_header()

# CSSでカードのデザインを調整
st.markdown("""
<style>
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin-top: 20px;
    }
    .stButton > button {
        width: 80px;
        height: 110px;
        font-size: 24px;
        border-radius: 8px;
        border: 2px solid #ddd;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        border-color: #2196F3;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if "concentration_state" not in st.session_state:
    st.session_state.concentration_state = GameState(cards=create_deck(13))

state = st.session_state.concentration_state

st.title("🎴 トランプ神経衰弱")

# --- スコア・状況表示 ---
col_s1, col_msg, col_s2 = st.columns([1, 2, 1])
with col_s1:
    render_result_box("Player 1", str(state.scores[0]), bg_color="#E3F2FD" if state.current_player == 0 else "#F5F5F5")
with col_s2:
    render_result_box("Player 2", str(state.scores[1]), bg_color="#E3F2FD" if state.current_player == 1 else "#F5F5F5")
with col_msg:
    st.markdown(f"### {state.message}")
    if state.game_over:
        if st.button("🔄 ゲームをリセットして新しく始める", use_container_width=True, type="primary"):
            st.session_state.concentration_state = GameState(cards=create_deck(13))
            st.rerun()

st.write("---")

# --- 盤面描画 ---
# 1行に何枚並べるか（PCは7枚、スマホは自動調整を期待）
cards_per_row = 7
rows = (len(state.cards) + cards_per_row - 1) // cards_per_row

for r in range(rows):
    cols = st.columns(cards_per_row)
    for c in range(cards_per_row):
        idx = r * cards_per_row + c
        if idx < len(state.cards):
            card = state.cards[idx]
            
            # カードのラベル（裏面か表面か）
            if card.is_matched:
                label = ""
                disabled = True
            elif card.is_flipped:
                label = card.display_value
                disabled = True
            else:
                label = "🎴"
                disabled = False
            
            # ボタンとして描画
            if cols[c].button(label, key=f"card_{idx}", disabled=disabled):
                st.session_state.concentration_state = handle_card_click(state, idx)
                st.rerun()

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定")
    if st.button("🚨 進行中のゲームをリセット", use_container_width=True):
        st.session_state.concentration_state = GameState(cards=create_deck(13))
        st.rerun()
    
    st.info("""
    **ルール:**
    - 2枚めくって同じ数字ならマッチ！
    - マッチしたら自分のスコアが加算され、もう一度引けます。
    - 数字が違ったら手番が交代します。
    """)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
