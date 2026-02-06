import streamlit as st
import random

st.set_page_config(page_title="双六メーカー", page_icon="🛤️")

if 'dice_total' not in st.session_state: st.session_state.dice_total = 0
if 'current_pos' not in st.session_state: st.session_state.current_pos = 0
if 'board_data' not in st.session_state: st.session_state.board_data = {}

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
