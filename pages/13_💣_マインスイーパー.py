import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.minesweeper import MinesweeperState, init_minesweeper_state
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_grid_board, render_page_header

st.set_page_config(page_title="マインスイーパー", page_icon="💣", layout="centered")

# グローバルスタイルの適用
render_page_header()

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "ms_state" not in st.session_state:
    saved_state = storage.get_item("ms_state_v2", is_json=True)
    if saved_state:
        st.session_state.ms_state = MinesweeperState(**saved_state)
    else:
        st.session_state.ms_state = init_minesweeper_state()

state: MinesweeperState = st.session_state.ms_state

st.markdown("<h1 style='text-align: center;'>💣 マインスイーパー</h1>", unsafe_allow_html=True)

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    ms_w = st.number_input("幅", 4, 20, state.width)
    ms_h = st.number_input("高さ", 4, 20, state.height)
    ms_mines = st.number_input("爆弾の数", 1, (ms_w * ms_h) - 1, state.num_mines)

    if st.button("ゲームをリセット", use_container_width=True, type="primary"):
        state.reset(ms_w, ms_h, ms_mines)
        storage.set_item("ms_state_v2", state.model_dump())
        st.rerun()

    st.write("---")
    ms_mode = st.radio("操作モード", ["🔓 オープン", "🚩 フラグ"], index=0, horizontal=True)

# --- メインエリア ---
# マインスイーパー風のスタイル
st.markdown(
    """
<style>
.stButton > button {
    aspect-ratio: 1;
    font-weight: 900 !important;
    font-size: 1.2rem !important;
    padding: 0 !important;
}
.num-1 { color: blue; }
.num-2 { color: green; }
.num-3 { color: red; }
.num-4 { color: darkblue; }
</style>
""",
    unsafe_allow_html=True,
)


def render_cell(idx):
    r, c = idx // state.width, idx % state.width
    is_revealed = state.revealed[r][c]
    is_flagged = state.flags[r][c]
    val = state.board[r][c]

    label = ""
    if is_revealed:
        if val == -1:
            label = "💣"
        elif val > 0:
            label = str(val)
        else:
            label = ""
    elif is_flagged:
        label = "🚩"

    # ボタンのスタイル
    disabled = is_revealed or state.status in ["won", "lost"]
    btn_type = "primary" if is_revealed else "secondary"

    if st.button(
        label if label else " ", key=f"ms_{r}_{c}", disabled=disabled, use_container_width=True, type=btn_type
    ):
        if ms_mode == "🔓 オープン":
            state.reveal_tile(r, c)
        else:
            state.toggle_flag(r, c)

        storage.set_item("ms_state_v2", state.model_dump())
        if state.status == "won":
            st.balloons()
        st.rerun()


# 盤面の描画
with st.container(border=True):
    render_grid_board(state.width * state.height, state.width, render_cell)

# 状態表示
if state.status == "won":
    st.success("🎉 クリア！おめでとうございます！")
elif state.status == "lost":
    st.error("💣 ドカン！ゲームオーバーです。")
else:
    st.info(f"🚩 残りの爆弾 (目安): {state.num_mines - sum(row.count(True) for row in state.flags)}")

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
