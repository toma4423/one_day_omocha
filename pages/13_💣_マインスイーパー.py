import numpy as np
import streamlit as st

from src.utils.minesweeper import create_board, is_game_won, reveal_tile
from src.utils.styles import render_donation_box, render_grid_board, render_page_header

st.set_page_config(page_title="マインスイーパー", page_icon="💣", layout="centered")

# グローバルスタイルの適用
render_page_header()

st.markdown("<h1 style='text-align: center;'>💣 マインスイーパー</h1>", unsafe_allow_html=True)

# セッション状態の初期化
if "ms_status" not in st.session_state:
    st.session_state.ms_status = "ready"


def init_minesweeper(w, h, mines):
    board = create_board(w, h, mines)
    st.session_state.ms_board = board
    st.session_state.ms_revealed = np.zeros((h, w), dtype=bool)
    st.session_state.ms_flags = np.zeros((h, w), dtype=bool)
    st.session_state.ms_status = "playing"


def reveal(r, c, w, h):
    st.session_state.ms_revealed = reveal_tile(
        r, c, w, h, st.session_state.ms_board, st.session_state.ms_revealed, st.session_state.ms_flags
    )


with st.sidebar:
    st.header("⚙️ 設定")
    ms_w = st.number_input("幅", 4, 15, 8)
    ms_h = st.number_input("高さ", 4, 15, 8)
    ms_mines = st.number_input("爆弾の数", 1, (ms_w * ms_h) - 1, 10)

    # サイズまたは爆弾の数が変わった場合にステータスをリセット
    if "ms_board" in st.session_state:
        current_mines = np.sum(st.session_state.ms_board == -1)
        if st.session_state.ms_board.shape != (ms_h, ms_w) or current_mines != ms_mines:
            st.session_state.ms_status = "ready"

    ms_mode = st.radio("操作モード", ["オープン 🔓", "フラグ 🚩"], index=0)
    if st.button("ゲームをリセット", use_container_width=True):
        st.session_state.ms_status = "ready"
        st.rerun()

# ゲームの初期化
if st.session_state.ms_status == "ready":
    init_minesweeper(ms_w, ms_h, ms_mines)


# 描画
def render_cell(idx):
    r, c = idx // ms_w, idx % ms_w
    label, disabled, key = "", False, f"ms_{r}_{c}"

    if st.session_state.ms_revealed[r, c]:
        val = st.session_state.ms_board[r, c]
        label = "💣" if val == -1 else (str(val) if val > 0 else "")
        disabled = True
    elif st.session_state.ms_flags[r, c]:
        label = "🚩"

    # ゲーム終了時の表示
    if st.session_state.ms_status in ["won", "lost"]:
        if st.session_state.ms_board[r, c] == -1:
            label = "💣"
        disabled = True

    # タイルの色設定 (Streamlitのボタンには直接色指定できないが、種別で分ける)
    btn_type = "secondary"
    if st.session_state.ms_revealed[r, c]:
        btn_type = "primary"

    if st.button(label if label else "　", key=key, disabled=disabled, use_container_width=True, type=btn_type):
        if ms_mode == "オープン 🔓":
            if st.session_state.ms_board[r, c] == -1:
                st.session_state.ms_status = "lost"
                st.error("ドカン！ゲームオーバー")
            else:
                reveal(r, c, ms_w, ms_h)
                # クリア判定
                if is_game_won(st.session_state.ms_board, st.session_state.ms_revealed):
                    st.session_state.ms_status = "won"
                    st.balloons()
                    st.success("クリア！おめでとう！")
        else:
            st.session_state.ms_flags[r, c] = not st.session_state.ms_flags[r, c]
        st.rerun()


with st.container(border=True):
    render_grid_board(ms_w * ms_h, ms_w, render_cell)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
