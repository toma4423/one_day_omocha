import streamlit as st
import random
import numpy as np

st.set_page_config(page_title="マインスイーパー", page_icon="💣")

if 'ms_status' not in st.session_state: st.session_state.ms_status = "ready"

st.title("💣 マインスイーパー")
with st.sidebar:
    ms_w, ms_h = st.number_input("幅", 4, 15, 8), st.number_input("高さ", 4, 15, 8)
    ms_mines = st.number_input("爆弾の数", 1, (ms_w * ms_h) - 1, 10)
    ms_mode = st.radio("操作モード", ["オープン", "フラグ 🚩"])
    if st.button("ゲームをリセット"):
        st.session_state.ms_status = "ready"
        st.rerun()
if st.session_state.ms_status == "ready":
    board = np.zeros((ms_h, ms_w), dtype=int)
    mines_pos = random.sample(range(ms_w * ms_h), ms_mines)
    for p in mines_pos: board[p // ms_w, p % ms_w] = -1
    for r in range(ms_h):
        for c in range(ms_w):
            if board[r, c] == -1: continue
            count = sum([1 for dr in [-1,0,1] for dc in [-1,0,1] if 0<=r+dr<ms_h and 0<=c+dc<ms_w and board[r+dr, c+dc]==-1])
            board[r, c] = count
    st.session_state.ms_board, st.session_state.ms_revealed, st.session_state.ms_flags, st.session_state.ms_status = board, np.zeros((ms_h, ms_w), dtype=bool), np.zeros((ms_h, ms_w), dtype=bool), "playing"
def reveal(r, c):
    if not (0 <= r < ms_h and 0 <= c < ms_w) or st.session_state.ms_revealed[r, c] or st.session_state.ms_flags[r, c]: return
    st.session_state.ms_revealed[r, c] = True
    if st.session_state.ms_board[r, c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]: reveal(r+dr, c+dc)
for r in range(ms_h):
    cols = st.columns(ms_w)
    for c in range(ms_w):
        with cols[c]:
            label, disabled, key = "", False, f"ms_{r}_{c}"
            if st.session_state.ms_revealed[r, c]:
                val = st.session_state.ms_board[r, c]
                label = "💣" if val == -1 else (str(val) if val > 0 else "")
                disabled = True
            elif st.session_state.ms_flags[r, c]: label = "🚩"
            if st.session_state.ms_status in ["won", "lost"]:
                if st.session_state.ms_board[r, c] == -1: label = "💣"
                disabled = True
            if st.button(label if label else "　", key=key, disabled=disabled, use_container_width=True):
                if ms_mode == "オープン":
                    if st.session_state.ms_board[r, c] == -1: st.session_state.ms_status = "lost"
                    else: reveal(r, c)
                else: st.session_state.ms_flags[r, c] = not st.session_state.ms_flags[r, c]
                st.rerun()
