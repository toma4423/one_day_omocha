import streamlit as st

from src.utils.concentration import GameState, create_deck, handle_card_click
from src.utils.styles import render_donation_box, render_page_header, render_result_box

st.set_page_config(page_title="神経衰弱", page_icon="🎴", layout="wide")

# グローバルスタイルの適用
render_page_header()

# CSSでカードのデザインを詳細に設定
st.markdown("""
<style>
    /* 共通のカードスタイル */
    .stButton > button {
        width: 100%;
        height: 100px;
        font-size: 28px;
        border-radius: 8px;
        transition: transform 0.1s, box-shadow 0.1s;
        font-weight: bold;
    }
    
    /* 赤いカード (ハート・ダイヤ) */
    div[data-testid="stBaseButton-secondary"] > button:has(span:contains("♥")),
    div[data-testid="stBaseButton-secondary"] > button:has(span:contains("♦")) {
        color: #D32F2F !important;
        background-color: #FFFFFF !important;
        border: 2px solid #D32F2F !important;
    }

    /* 黒いカード (スペード・クローバー) - 白文字にするための設定 */
    div[data-testid="stBaseButton-secondary"] > button:has(span:contains("♠")),
    div[data-testid="stBaseButton-secondary"] > button:has(span:contains("♣")) {
        color: #FFFFFF !important;
        background-color: #333333 !important;
        border: 2px solid #000000 !important;
    }

    /* 裏面 */
    div[data-testid="stBaseButton-secondary"] > button:has(span:contains("🎴")) {
        background-color: #455A64 !important;
        color: #CFD8DC !important;
        border: 2px solid #37474F !important;
    }
    
    /* マッチしたカード（透明化） */
    div[data-testid="stBaseButton-secondary"] > button:disabled {
        opacity: 0.3;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if "concentration_state" not in st.session_state:
    st.session_state.concentration_state = GameState(cards=create_deck(13, use_all_suits=False))

state = st.session_state.concentration_state

st.title("🎴 トランプ神経衰弱")

# --- スコア・状況表示 ---
col_s1, col_msg, col_s2 = st.columns([1, 2, 1])
with col_s1:
    # アクティブな方をオレンジ色にする
    is_active = (state.current_player == 0)
    render_result_box(
        "Player 1",
        str(state.scores[0]),
        bg_color="#FFF3E0" if is_active else "#F5F5F5",
        text_color="#FB8C00" if is_active else "#757575",
        border_color="#FB8C00" if is_active else "#E0E0E0",
    )
with col_s2:
    is_active = (state.current_player == 1)
    render_result_box(
        "Player 2",
        str(state.scores[1]),
        bg_color="#FFF3E0" if is_active else "#F5F5F5",
        text_color="#FB8C00" if is_active else "#757575",
        border_color="#FB8C00" if is_active else "#E0E0E0",
    )
with col_msg:
    st.markdown(f"### {state.message}")
    if state.game_over:
        if st.button("🔄 もう一度遊ぶ", use_container_width=True, type="primary"):
            st.session_state.concentration_state = GameState(cards=create_deck(13, use_all_suits=state.use_all_suits), use_all_suits=state.use_all_suits)
            st.rerun()

st.write("---")

# --- 盤面描画 ---
# デッキ枚数に応じて列数を調整
cards_per_row = 13 if state.use_all_suits else 7
rows = (len(state.cards) + cards_per_row - 1) // cards_per_row

for r in range(rows):
    cols = st.columns(cards_per_row)
    for c in range(cards_per_row):
        idx = r * cards_per_row + c
        if idx < len(state.cards):
            card = state.cards[idx]
            
            if card.is_matched:
                label = card.display_value # マッチしたカードも見せておく（薄く表示）
                disabled = True
            elif card.is_flipped:
                label = card.display_value
                disabled = True
            else:
                label = "🎴"
                disabled = False
            
            if cols[c].button(label, key=f"card_{idx}", disabled=disabled, use_container_width=True):
                st.session_state.concentration_state = handle_card_click(state, idx)
                st.rerun()

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定・難易度")
    
    # 難易度選択
    mode_options = ["初級 (♠/♥ 26枚)", "上級 (全て 52枚)"]
    current_mode_idx = 1 if state.use_all_suits else 0
    new_mode_str = st.radio("使用するスート", options=mode_options, index=current_mode_idx)
    new_use_all = (new_mode_str == mode_options[1])
    
    if new_use_all != state.use_all_suits:
        if st.button("⚠️ 設定を反映してリセット"):
            st.session_state.concentration_state = GameState(cards=create_deck(13, use_all_suits=new_use_all), use_all_suits=new_use_all)
            st.rerun()

    if st.button("🚨 ゲームを強制リセット", use_container_width=True):
        st.session_state.concentration_state = GameState(cards=create_deck(13, use_all_suits=state.use_all_suits), use_all_suits=state.use_all_suits)
        st.rerun()
    
    st.info("""
    **ルール:**
    - 2枚めくって同じ数字ならマッチ！
    - マッチしたら自分のスコアが加算され、もう一度引けます。
    - 数字が違ったら手番が交代します。
    - **♠♣は黒背景/白文字、♥♦は白背景/赤文字** です。
    """)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
