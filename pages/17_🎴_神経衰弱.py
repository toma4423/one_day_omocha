import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.concentration import ConcentrationGameState, create_deck, handle_card_click
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_result_box,
    render_storage_controls,
    wait_for_storage_load,
)

st.set_page_config(page_title="神経衰弱", page_icon="🎴", layout="wide")

# グローバルスタイルの適用
render_page_header()

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "_concentration_initialized" not in st.session_state:
    saved_state = wait_for_storage_load(storage, "concentration_state_v2", "_concentration_initialized")
    if saved_state:
        st.session_state.concentration_state = ConcentrationGameState(**saved_state)
    else:
        st.session_state.concentration_state = ConcentrationGameState(
            cards=create_deck(13, use_all_suits=False), mode="battle", use_all_suits=False
        )
    st.rerun()

state: ConcentrationGameState = st.session_state.concentration_state

# 基本的なカードスタイル定義
st.markdown(
    """
<style>
    /* 盤面（メインエリア）のカードボタンのみに適用 */
    [data-testid="stMain"] .stButton > button {
        width: 100% !important;
        max-width: 80px !important;
        aspect-ratio: 5 / 7 !important;
        height: auto !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        transition: all 0.2s !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        padding: 0 !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* カード裏面 - メインエリアのみ */
    [data-testid="stMain"] .card-back button {
        background: linear-gradient(135deg, #2C3E50 25%, #34495E 25%, #34495E 50%, #2C3E50 50%, #2C3E50 75%, #34495E 75%, #34495E 100%) !important;
        background-size: 10px 10px !important;
        border: 2px solid #ECF0F1 !important;
        color: white !important;
        font-size: 1.5rem !important;
    }

    /* カード表面 - 赤 (ボタンとその中のテキスト両方に適用) */
    [data-testid="stMain"] .card-front-red button,
    [data-testid="stMain"] .card-front-red button p {
        background-color: #FFFFFF !important;
        color: #D32F2F !important;
        border-color: #D32F2F !important;
    }
    
    /* カード表面 - 黒 */
    [data-testid="stMain"] .card-front-black button,
    [data-testid="stMain"] .card-front-black button p {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border-color: #1A1A1A !important;
    }

    /* 獲得済み - メインエリアのみ */
    [data-testid="stMain"] .card-matched button {
        background-color: #F9F9F9 !important;
        color: #DDDDDD !important;
        border: 1px dashed #EEEEEE !important;
        opacity: 0.4 !important;
    }

    /* 改行設定 - メインエリアのみ */
    [data-testid="stMain"] .stButton > button div p {
        white-space: pre-line !important;
        line-height: 1.1 !important;
        font-size: 1.2rem !important;
    }

    /* カラム間の隙間を詰める */
    [data-testid="column"] {
        padding: 0 2px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🎴 トランプ神経衰弱")

# --- スコア・状況表示 ---
col_s1, col_msg, col_s2 = st.columns([1, 2, 1])

with col_s1:
    if state.mode == "battle":
        is_active = state.current_player == 0
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
        is_active = state.current_player == 1
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
            st.session_state.concentration_state = ConcentrationGameState(
                cards=create_deck(13, use_all_suits=state.use_all_suits),
                use_all_suits=state.use_all_suits,
                mode=state.mode,
            )
            st.rerun()

st.write("---")

# --- 盤面描画 ---
cards_per_row = 10 if state.use_all_suits else 7
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
                    st.markdown("</div>", unsafe_allow_html=True)
                elif card.is_flipped:
                    # 表
                    color_class = "red" if card.is_red else "black"
                    st.markdown(f'<div class="card-front-{color_class}">', unsafe_allow_html=True)
                    # 改行を入れて縦に並べる
                    label = f"{card.rank}\n{card.suit}"
                    st.button(label, key=f"card_{idx}", disabled=True, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    # 裏（クリック可能）
                    st.markdown('<div class="card-back">', unsafe_allow_html=True)
                    if st.button("？", key=f"card_{idx}", use_container_width=True):
                        st.session_state.concentration_state = handle_card_click(state, idx)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

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
    new_use_all = selected_suit_label == suit_options[1]

    # 設定の反映
    if new_mode != state.mode or new_use_all != state.use_all_suits:
        if st.button("⚠️ 設定を反映してリセット"):
            st.session_state.concentration_state = ConcentrationGameState(
                cards=create_deck(13, use_all_suits=new_use_all), use_all_suits=new_use_all, mode=new_mode
            )
            st.rerun()

    if st.button("🚨 ゲームをリセット", use_container_width=True):
        st.session_state.concentration_state = ConcentrationGameState(
            cards=create_deck(13, use_all_suits=state.use_all_suits), use_all_suits=state.use_all_suits, mode=state.mode
        )
        st.rerun()

    st.info("""
    **ルール:**
    - めくったカードが同じ数字なら「GET」になります。
    - **対戦モード**: マッチするともう一度引けます。
    - **1人モード**: すべてめくるまでの手数を競います。
    """)


# データの管理
def on_load(data):
    st.session_state.concentration_state = ConcentrationGameState(**data)


render_storage_controls(
    storage=storage,
    storage_key="concentration_state_v2",
    current_data=state,
    on_load_callback=on_load,
    file_prefix="concentration",
    is_pydantic=True,
)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
