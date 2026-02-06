import streamlit as st
import random
import numpy as np

# ページの設定
st.set_page_config(page_title="今日のおもちゃ", layout="wide")

# セッション状態の初期化
# カウント用
if 'cs_x' not in st.session_state: st.session_state.cs_x = 0
if 'cs_y' not in st.session_state: st.session_state.cs_y = 0
if 'cs_z' not in st.session_state: st.session_state.cs_z = 0
# 倍率用
if 'cs_weight_x' not in st.session_state: st.session_state.cs_weight_x = 1.0
if 'cs_weight_y' not in st.session_state: st.session_state.cs_weight_y = 1.0
if 'cs_weight_z' not in st.session_state: st.session_state.cs_weight_z = 1.0

if 'dice_total' not in st.session_state: st.session_state.dice_total = 0
if 'current_pos' not in st.session_state: st.session_state.current_pos = 0
if 'board_data' not in st.session_state: st.session_state.board_data = {}
if 'kurohige_status' not in st.session_state: st.session_state.kurohige_status = "ready"
if 'ms_status' not in st.session_state: st.session_state.ms_status = "ready"

# カウントサポート用UI
def weighted_counter_ui(label, key_val, key_weight):
    st.markdown(f"#### {label}")
    col_val, col_w = st.columns([2, 1])
    with col_val:
        # 入力欄のみ表示
        val = st.number_input(f"{label}の数", value=st.session_state[key_val], key=f"input_{key_val}")
        st.session_state[key_val] = val
    with col_w:
        weight = st.number_input(f"{label}の倍率", value=st.session_state[key_weight], key=f"input_{key_weight}", step=0.1)
        st.session_state[key_weight] = weight
    
    current_weighted = val * weight
    st.caption(f"現在の{label}値: {current_weighted:.1f}")
    return current_weighted

# サイドバーの作成
st.sidebar.title("おもちゃ箱")
page = st.sidebar.selectbox("おもちゃを選んでね", ["ホーム", "サイコロ", "双六メーカー", "黒ひげ危機一発", "マインスイーパー", "カウントサポート"])

if page == "ホーム":
    st.markdown("<h1 style='text-align: center; margin-top: 10vh;'>今日のおもちゃ</h1>", unsafe_allow_html=True)
    st.write("---")
    st.write("サイドバーからおもちゃを選んで遊んでね！")

elif page == "サイコロ":
    st.title("🎲 サイコロ")
    col1, col2 = st.columns(2)
    with col1: x = st.number_input("ダイスの数 (x)", 1, 100, 1)
    with col2: n = st.number_input("ダイスの目の数 (n)", 1, 1000, 6)
    if st.button("サイコロを振る！", use_container_width=True):
        total = sum([random.randint(1, n) for _ in range(x)])
        st.write("---")
        st.markdown(f"<h3 style='text-align: center;'>結果</h3><h1 style='text-align: center;'>{total}</h1>", unsafe_allow_html=True)
        st.balloons()

elif page == "双六メーカー":
    st.title("🛤️ 双六メーカー")
    with st.sidebar:
        with st.expander("盤面の設定"):
            board_type = st.radio("形式を選択", ["スタートからゴール", "循環型（ループ）"])
            num_tiles = st.slider("マスの数", 3, 50, 10)
            if st.button("盤面を初期化"):
                st.session_state.board_data, st.session_state.current_pos, st.session_state.dice_total = {}, 0, 0
                st.rerun()
        st.write("---")
        st.subheader("🎲 サイコロを振る")
        x_dice = st.number_input("ダイスの数 (x)", 1, 10, 1)
        n_dice = st.number_input("面の数 (n)", 1, 100, 6)
        if st.button("サイコロを振る！", use_container_width=True):
            st.session_state.dice_total = sum([random.randint(1, n_dice) for _ in range(x_dice)])
            st.balloons()
    total_tiles = num_tiles if board_type == "スタートからゴール" else num_tiles + 1
    for i in range(total_tiles):
        key = f"tile_{i}"
        if key not in st.session_state.board_data:
            if board_type == "スタートからゴール":
                if i == 0: st.session_state.board_data[key] = "🚩 START"
                elif i == num_tiles - 1: st.session_state.board_data[key] = "🏆 GOAL"
                else: st.session_state.board_data[key] = f"マス {i}"
            else:
                st.session_state.board_data[key] = "🔄 循環" if i == num_tiles else f"マス {i+1}"
    if st.session_state.dice_total > 0:
        st.markdown(f"<div style='background-color:#E3F2FD;padding:20px;border-radius:10px;text-align:center;margin-bottom:20px;border:2px solid #2196F3;'><span style='font-size:20px;color:#1565C0;'>🎲 出目:</span><span style='font-size:48px;font-weight:bold;color:#0D47A1;margin-left:20px;'>{st.session_state.dice_total}</span></div>", unsafe_allow_html=True)
    st.subheader("双六盤面")
    cols_per_row = 5
    for i in range(0, total_tiles, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < total_tiles:
                key = f"tile_{idx}"
                with col:
                    is_curr = st.session_state.current_pos == idx
                    st.markdown(f"<div style='border:3px solid {'#F44336' if is_curr else '#ccc'};border-radius:10px;padding:5px;text-align:center;background-color:{'#FFEB3B' if is_curr else '#f9f9f9'};margin-bottom:5px;color:black;'><small>{'📍 現在地' if is_curr else f'No. {idx+1}'}</small></div>", unsafe_allow_html=True)
                    st.session_state.board_data[key] = st.text_input(f"t_{idx}", st.session_state.board_data[key], key=f"in_{idx}", label_visibility="collapsed")
                    if st.button("移動", key=f"b_{idx}", use_container_width=True):
                        st.session_state.current_pos = idx
                        st.rerun()
                    if idx < total_tiles - 1: st.markdown("<div style='text-align:center;'>👇</div>" if (j+1)%cols_per_row==0 else "<div style='text-align:center;'>👉</div>", unsafe_allow_html=True)

elif page == "黒ひげ危機一発":
    st.title("☠️ 黒ひげ危機一発")
    num_slots = st.sidebar.slider("穴の数", 4, 24, 12)
    if st.session_state.kurohige_status == "ready" or st.sidebar.button("リセット"):
        st.session_state.kurohige_target, st.session_state.kurohige_clicked, st.session_state.kurohige_status = random.randint(0, num_slots - 1), [], "playing"
        st.rerun()
    if st.session_state.kurohige_status == "boom":
        st.markdown("<h1 style='text-align:center;font-size:100px;'>🚀 🏴‍☠️</h1><h2 style='text-align:center;color:red;'>ドカン！！！</h2>", unsafe_allow_html=True)
        st.snow()
    else: st.markdown("<h1 style='text-align:center;font-size:100px;'>🛢️</h1>", unsafe_allow_html=True)
    cols_per_row = 4
    for i in range(0, num_slots, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < num_slots:
                with col:
                    if idx in st.session_state.kurohige_clicked: st.button("🗡️", key=f"k_{idx}", disabled=True, use_container_width=True)
                    elif st.session_state.kurohige_status == "boom": st.button("🕳️", key=f"k_{idx}", disabled=True, use_container_width=True)
                    else:
                        if st.button("❓", key=f"k_{idx}", use_container_width=True):
                            if idx == st.session_state.kurohige_target: st.session_state.kurohige_status = "boom"
                            else: st.session_state.kurohige_clicked.append(idx)
                            st.rerun()

elif page == "マインスイーパー":
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

elif page == "カウントサポート":
    st.title("🔢 カウントサポート")
    
    col_main1, col_space, col_main2 = st.columns([2, 0.5, 2])
    
    with col_main1:
        st.subheader("基本カウント")
        val_x = weighted_counter_ui("X", "cs_x", "cs_weight_x")
        val_y = weighted_counter_ui("Y", "cs_y", "cs_weight_y")
        
        st.write("---")
        diff_xy = val_x - val_y
        st.markdown(f"### X - Y (算出値)")
        st.markdown(f"<div style='background-color:#2196F3;padding:20px;border-radius:10px;text-align:center;font-size:48px;font-weight:bold;color:white;border:2px solid #0D47A1;'>{diff_xy:.1f}</div>", unsafe_allow_html=True)

    with col_main2:
        st.subheader("追加カウント")
        val_z = weighted_counter_ui("Z", "cs_z", "cs_weight_z")
        
        st.write("---")
        final_result = diff_xy - val_z
        st.markdown(f"### (X - Y) - Z")
        st.markdown(f"<div style='background-color:#E8F5E9;padding:20px;border-radius:10px;text-align:center;font-size:64px;font-weight:bold;color:#2E7D32;border:2px solid #2E7D32;'>{final_result:.1f}</div>", unsafe_allow_html=True)

    if st.sidebar.button("全ての数値をリセット"):
        # 論理的な値と、number_inputの内部状態（key）の両方をリセット
        for k in ["cs_x", "cs_y", "cs_z"]: 
            st.session_state[k] = 0
            if f"input_{k}" in st.session_state: st.session_state[f"input_{k}"] = 0
        for k in ["cs_weight_x", "cs_weight_y", "cs_weight_z"]: 
            st.session_state[k] = 1.0
            if f"input_{k}" in st.session_state: st.session_state[f"input_{k}"] = 1.0
        st.rerun()