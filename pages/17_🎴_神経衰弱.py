import streamlit as st

from src.utils.concentration import GameState, create_deck, handle_card_click
from src.utils.styles import render_donation_box, render_page_header, render_result_box

st.set_page_config(page_title="神経衰弱", page_icon="🎴", layout="wide")

# グローバルスタイルの適用
render_page_header()

# 基本的なカードスタイル定義
st.markdown("""
<style>
    /* 共通のカードスタイル */
    .stButton > button {
        width: 100%;
        height: 100px;
        font-size: 24px;
        border-radius: 8px;
        transition: transform 0.1s;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* マッチした「GET」カードの共通スタイル */
    .matched-card > button {
        background-color: #E0E0E0 !important;
        color: #9E9E9E !important;
        border: 2px dashed #BDBDBD !important;
        font-size: 18px !important;
    }

    /* 裏面カードの共通スタイル */
    .back-card > button {
        background-color: #2C3E50 !important;
        color: #ECF0F1 !important;
        border: 2px solid #34495E !important;
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
ORANGE_COLOR = "#FF9800"
GRAY_COLOR = "#757575"

with col_s1:
    is_active = (state.current_player == 0)
    render_result_box(
        "Player 1",
        str(state.scores[0]),
        bg_color="#FFF3E0" if is_active else "#F5F5F5",
        text_color=ORANGE_COLOR if is_active else GRAY_COLOR,
        border_color=ORANGE_COLOR if is_active else "#E0E0E0",
    )
with col_s2:
    is_active = (state.current_player == 1)
    render_result_box(
        "Player 2",
        str(state.scores[1]),
        bg_color="#FFF3E0" if is_active else "#F5F5F5",
        text_color=ORANGE_COLOR if is_active else GRAY_COLOR,
        border_color=ORANGE_COLOR if is_active else "#E0E0E0",
    )
with col_msg:
    st.markdown(f"<h3 style='text-align:center;'>{state.message}</h3>", unsafe_allow_html=True)
    if state.game_over:
        if st.button("🔄 もう一度遊ぶ", use_container_width=True, type="primary"):
            st.session_state.concentration_state = GameState(cards=create_deck(13, use_all_suits=state.use_all_suits), use_all_suits=state.use_all_suits)
            st.rerun()

st.write("---")

# --- 盤面描画 ---
cards_per_row = 13 if state.use_all_suits else 7
rows = (len(state.cards) + cards_per_row - 1) // cards_per_row

for r in range(rows):
    cols = st.columns(cards_per_row)
    for c in range(cards_per_row):
        idx = r * cards_per_row + c
        if idx < len(state.cards):
            card = state.cards[idx]
            
            # 状態に応じたラベルとスタイルの決定
            if card.is_matched:
                label = "GET"
                container_class = "matched-card"
                disabled = True
            elif card.is_flipped:
                label = card.display_value
                container_class = "front-card"
                disabled = True
                # めくられた時の色を動的に適用
                if card.is_red:
                    # ハート・ダイヤ: 白背景に赤文字
                    text_c, bg_c, border_c = "#D32F2F", "#FFFFFF", "#D32F2F"
                else:
                    # スペード・クローバー: 黒背景に白文字
                    text_c, bg_c, border_c = "#FFFFFF", "#333333", "#000000"
                
                st.markdown(f"""
                <style>
                    div[data-testid="column"]:nth-child({c+1}) div[data-testid="stVerticalBlock"] > div:nth-child({r+1}) button {{
                        color: {text_c} !important;
                        background-color: {bg_c} !important;
                        border: 2px solid {border_c} !important;
                    }}
                </style>
                """, unsafe_allow_html=True)
            else:
                label = "🎴"
                container_class = "back-card"
                disabled = False
            
            # カードをボタンとして配置（コンテナクラスでラップ）
            with cols[c]:
                st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
                if st.button(label, key=f"card_{idx}", disabled=disabled, use_container_width=True):
                    st.session_state.concentration_state = handle_card_click(state, idx)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定・難易度")
    
    mode_options = ["初級 (2スート・26枚)", "上級 (全スート・52枚)"]
    current_mode_idx = 1 if state.use_all_suits else 0
    new_mode_str = st.radio("使用するカード", options=mode_options, index=current_mode_idx)
    new_use_all = (new_mode_str == mode_options[1])
    
    if new_use_all != state.use_all_suits:
        if st.button("⚠️ 設定を反映してリセット"):
            st.session_state.concentration_state = GameState(cards=create_deck(13, use_all_suits=new_use_all), use_all_suits=new_use_all)
            st.rerun()

    if st.button("🚨 ゲームをリセット", use_container_width=True):
        st.session_state.concentration_state = GameState(cards=create_deck(13, use_all_suits=state.use_all_suits), use_all_suits=state.use_all_suits)
        st.rerun()
    
    st.info("""
    **ルール:**
    - めくったカードが同じ数字なら「GET」になります。
    - **♠♣**: 黒背景に白文字
    - **♥♦**: 白背景に赤文字
    - 操作中のプレイヤーは**オレンジ色**で表示されます。
    """)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
