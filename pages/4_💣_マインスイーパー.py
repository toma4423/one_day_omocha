import streamlit as st
import random
import numpy as np

st.set_page_config(page_title="マインスイーパー", page_icon="💣")

# セッション状態の初期化
if 'ms_status' not in st.session_state:
    st.session_state.ms_status = "ready"

def init_minesweeper(w, h, mines):
    board = np.zeros((h, w), dtype=int)
    mines_pos = random.sample(range(w * h), mines)
    for p in mines_pos:
        board[p // w, p % w] = -1
    
    # 周囲の爆弾数を計算
    for r in range(h):
        for c in range(w):
            if board[r, c] == -1:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if 0 <= r + dr < h and 0 <= c + dc < w:
                        if board[r + dr, c + dc] == -1:
                            count += 1
            board[r, c] = count
            
    st.session_state.ms_board = board
    st.session_state.ms_revealed = np.zeros((h, w), dtype=bool)
    st.session_state.ms_flags = np.zeros((h, w), dtype=bool)
    st.session_state.ms_status = "playing"

def reveal(r, c, w, h):
    if not (0 <= r < h and 0 <= c < w):
        return
    if st.session_state.ms_revealed[r, c] or st.session_state.ms_flags[r, c]:
        return
    
    st.session_state.ms_revealed[r, c] = True
    
    # 0の場合は周囲も開く
    if st.session_state.ms_board[r, c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                reveal(r + dr, c + dc, w, h)

st.title("💣 マインスイーパー")

with st.sidebar:
    ms_w = st.number_input("幅", 4, 15, 8)
    ms_h = st.number_input("高さ", 4, 15, 8)
    ms_mines = st.number_input("爆弾の数", 1, (ms_w * ms_h) - 1, 10)
    ms_mode = st.radio("操作モード", ["オープン", "フラグ 🚩"])
    if st.button("ゲームをリセット"):
        st.session_state.ms_status = "ready"
        st.rerun()

# ゲームの初期化
if st.session_state.ms_status == "ready":
    init_minesweeper(ms_w, ms_h, ms_mines)

# 描画
for r in range(ms_h):
    cols = st.columns(ms_w)
    for c in range(ms_w):
        with cols[c]:
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
            
            if st.button(label if label else "　", key=key, disabled=disabled, use_container_width=True):
                if ms_mode == "オープン":
                    if st.session_state.ms_board[r, c] == -1:
                        st.session_state.ms_status = "lost"
                        st.error("ドカン！ゲームオーバー")
                    else:
                        reveal(r, c, ms_w, ms_h)
                        # クリア判定
                        unrevealed_safe = np.sum((st.session_state.ms_board != -1) & (~st.session_state.ms_revealed))
                        if unrevealed_safe == 0:
                            st.session_state.ms_status = "won"
                            st.balloons()
                            st.success("クリア！おめでとう！")
                else:
                    st.session_state.ms_flags[r, c] = not st.session_state.ms_flags[r, c]
                st.rerun()
