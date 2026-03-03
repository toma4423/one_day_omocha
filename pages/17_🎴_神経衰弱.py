import streamlit as st

from src.utils.concentration import GameState, create_deck, handle_card_click
from src.utils.styles import render_donation_box, render_page_header, render_result_box

st.set_page_config(page_title="神経衰弱", page_icon="🎴", layout="wide")

# グローバルスタイルの適用
render_page_header()

# 基本的なカードスタイル定義
st.markdown("""
<style>
    /* カードの基本サイズと形状 */
    .stButton > button {
        height: 140px;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.2s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 5px !important;
    }
    
    /* カード裏面（未選択） */
    .card-back button {
        background: linear-gradient(135deg, #2C3E50 25%, #34495E 25%, #34495E 50%, #2C3E50 50%, #2C3E50 75%, #34495E 75%, #34495E 100%) !important;
        background-size: 20px 20px !important;
        border: 4px solid #ECF0F1 !important;
        color: white !important;
        font-size: 40px !important;
    }
    .card-back button:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        border-color: #FFFFFF !important;
    }

    /* カード表面（めくられた状態）- 共通 */
    .card-front button {
        background-color: #FFFFFF !important;
        border: 2px solid #333 !important;
        font-size: 24px !important;
        cursor: default !important;
    }
    
    /* 赤いスート（ハート・ダイヤ） */
    .card-front-red button {
        color: #D32F2F !important;
        border-color: #D32F2F !important;
    }
    
    /* 黒いスート（スペード・クローバー） */
    .card-front-black button {
        color: #1A1A1A !important;
        border-color: #1A1A1A !important;
    }

    /* 獲得済みカード */
    .card-matched button {
        background-color: #F5F5F5 !important;
        color: #BDBDBD !important;
        border: 2px dashed #E0E0E0 !important;
        opacity: 0.6;
        cursor: default !important;
        box-shadow: none !important;
    }

    /* カード内のランクとスートの配置用 */
    .card-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100%;
        position: relative;
    }
    .rank-top {
        position: absolute;
        top: 5px;
        left: 5px;
        font-size: 18px;
    }
    .suit-large {
        font-size: 48px;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if "concentration_state" not in st.session_state or not hasattr(st.session_state.concentration_state, "mode"):
    st.session_state.concentration_state = GameState(
        cards=create_deck(13, use_all_suits=False),
        mode="battle"
    )

state = st.session_state.concentration_state

st.title("🎴 トランプ神経衰弱")

# --- スコア・状況表示 ---
col_s1, col_msg, col_s2 = st.columns([1, 2, 1])

with col_s1:
    if state.mode == "battle":
        is_active = (state.current_player == 0)
        render_result_box(
            "Player 1",
            str(state.scores[0]),
            bg_color="#FFF3E0" if is_active else "#F5F5F5",
            text_color="#FF9800" if is_active else "#757575",
            border_color="#FF9800" if is_active else "#E0E0E0",
        )
    else:
        render_result_box(
            "Matches",
            str(state.scores[0]),
            bg_color="#E3F2FD",
            text_color="#1976D2",
            border_color="#1976D2",
        )

with col_s2:
    if state.mode == "battle":
        is_active = (state.current_player == 1)
        render_result_box(
            "Player 2",
            str(state.scores[1]),
            bg_color="#FFF3E0" if is_active else "#F5F5F5",
            text_color="#FF9800" if is_active else "#757575",
            border_color="#FF9800" if is_active else "#E0E0E0",
        )
    else:
        render_result_box(
            "Moves",
            str(state.move_count),
            bg_color="#F5F5F5",
            text_color="#424242",
            border_color="#E0E0E0",
        )

with col_msg:
    st.markdown(f"<h3 style='text-align:center;'>{state.message}</h3>", unsafe_allow_html=True)
    if state.game_over:
        if st.button("🔄 もう一度遊ぶ", use_container_width=True, type="primary"):
            st.session_state.concentration_state = GameState(
                cards=create_deck(13, use_all_suits=state.use_all_suits),
                use_all_suits=state.use_all_suits,
                mode=state.mode
            )
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
            
            with cols[c]:
                if card.is_matched:
                    # マッチ済み
                    st.markdown('<div class="card-matched">', unsafe_allow_html=True)
                    st.button("GET", key=f"card_{idx}", disabled=True, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                elif card.is_flipped:
                    # 表
                    color_class = "red" if card.is_red else "black"
                    st.markdown(f'<div class="card-front card-front-{color_class}">', unsafe_allow_html=True)
                    # HTMLタグを含めたボタンラベルはStreamlitでは非推奨だが、絵文字とテキストならある程度可能
                    # 複雑なレイアウトはCSSでボタンの中身を模倣する
                    label = f"{card.suit}\n{card.rank}"
                    st.button(label, key=f"card_{idx}", disabled=True, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # 裏（クリック可能）
                    st.markdown('<div class="card-back">', unsafe_allow_html=True)
                    if st.button("？", key=f"card_{idx}", use_container_width=True):
                        st.session_state.concentration_state = handle_card_click(state, idx)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定・モード")
    
    # モード選択
    mode_map = {"1人プレイ": "single", "2人対戦": "battle"}
    mode_labels = list(mode_map.keys())
    current_mode_idx = 1 if state.mode == "battle" else 0
    selected_label = st.radio("ゲームモード", options=mode_labels, index=current_mode_idx)
    new_mode = mode_map[selected_label]
    
    # カード枚数選択
    suit_options = ["初級 (2スート・26枚)", "上級 (全スート・52枚)"]
    current_suit_idx = 1 if state.use_all_suits else 0
    selected_suit_label = st.radio("カード枚数", options=suit_options, index=current_suit_idx)
    new_use_all = (selected_suit_label == suit_options[1])
    
    if new_mode != state.mode or new_use_all != state.use_all_suits:
        if st.button("⚠️ 設定を反映してリセット"):
            st.session_state.concentration_state = GameState(
                cards=create_deck(13, use_all_suits=new_use_all),
                use_all_suits=new_use_all,
                mode=new_mode
            )
            st.rerun()

    if st.button("🚨 ゲームをリセット", use_container_width=True):
        st.session_state.concentration_state = GameState(
            cards=create_deck(13, use_all_suits=state.use_all_suits),
            use_all_suits=state.use_all_suits,
            mode=state.mode
        )
        st.rerun()
    
    st.info("""
    **ルール:**
    - めくったカードが同じ数字なら「GET」になります。
    - **対戦モード**: マッチするともう一度引けます。
    - **1人モード**: すべてめくるまでの手数を競います。
    """)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
