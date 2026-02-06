import streamlit as st
import random
import numpy as np

# ページの設定
st.set_page_config(page_title="今日のおもちゃ", layout="wide")

# セッション状態の初期化
for key in ['dice_total', 'current_pos', 'cs_x', 'cs_y', 'cs_z']:
    if key not in st.session_state: st.session_state[key] = 0
if 'board_data' not in st.session_state: st.session_state.board_data = {}

# 他のゲームの状態初期化
if 'kurohige_status' not in st.session_state: st.session_state.kurohige_status = "ready"
if 'ms_status' not in st.session_state: st.session_state.ms_status = "ready"

# サイドバーの作成
st.sidebar.title("おもちゃ箱")
page = st.sidebar.selectbox("おもちゃを選んでね", ["ホーム", "サイコロ", "双六メーカー", "黒ひげ危機一発", "マインスイーパー", "カウントサポート"])

# 汎用カウンター関数
def counter_ui(label, key_name):
    st.markdown(f"#### {label}")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("ー", key=f"minus_{key_name}", use_container_width=True):
            st.session_state[key_name] -= 1
            st.rerun()
    with c2:
        st.session_state[key_name] = st.number_input(label, value=st.session_state[key_name], key=f"input_{key_name}", label_visibility="collapsed")
    with c3:
        if st.button("＋", key=f"plus_{key_name}", use_container_width=True):
            st.session_state[key_name] += 1
            st.rerun()

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
    if st.session_state.kurohige_status == "boom" and st.button("もう一度遊ぶ", use_container_width=True):
        st.session_state.kurohige_status = "ready"; st.rerun()

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
    if st.session_state.ms_status == "playing" and np.sum(st.session_state.ms_revealed) == (ms_w * ms_h) - ms_mines:
        st.session_state.ms_status = "won"
    if st.session_state.ms_status == "won": st.success("🎉 クリア！"); st.balloons()
    elif st.session_state.ms_status == "lost": st.error("💥 ゲームオーバー")
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
    
    # 左右の余白を抑えたカラム構成
    col_main1, col_space, col_main2 = st.columns([2, 1, 2])
    
    with col_main1:
        st.subheader("基本カウント")
        counter_ui("X", "cs_x")
        counter_ui("Y", "cs_y")
        
        st.write("---")
        diff_xy = st.session_state.cs_x - st.session_state.cs_y
        st.markdown(f"### X - Y")
        st.markdown(f"<div style='background-color:#2196F3;padding:20px;border-radius:10px;text-align:center;font-size:48px;font-weight:bold;color:white;border:2px solid #0D47A1;'>{diff_xy}</div>", unsafe_allow_html=True)

    with col_main2:
        st.subheader("追加カウント")
        counter_ui("Z", "cs_z")
        
        st.write("---")
        final_result = diff_xy - st.session_state.cs_z
        st.markdown(f"### (X - Y) - Z")
        st.markdown(f"<div style='background-color:#E8F5E9;padding:20px;border-radius:10px;text-align:center;font-size:64px;font-weight:bold;color:#2E7D32;border:2px solid #2E7D32;'>{final_result}</div>", unsafe_allow_html=True)

    if st.sidebar.button("全ての数値をリセット"):
        st.session_state.cs_x, st.session_state.cs_y, st.session_state.cs_z = 0, 0, 0
        st.rerun()