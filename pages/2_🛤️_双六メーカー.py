import streamlit as st
from src.utils.dice import roll_dice
from src.utils.styles import render_styled_number

st.set_page_config(page_title="双六メーカー", page_icon="🛤️")

# セッション状態の初期化
if 'dice_total' not in st.session_state:
    st.session_state.dice_total = 0
if 'current_pos' not in st.session_state:
    st.session_state.current_pos = 0
if 'board_data' not in st.session_state:
    st.session_state.board_data = {}

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
        results = roll_dice(x_dice, n_dice)
        st.session_state.dice_total = sum(results)
        st.balloons()

total_tiles = num_tiles if board_type == "スタートからゴール" else num_tiles + 1

# 盤面データの初期化
for i in range(total_tiles):
    key = f"tile_{i}"
    if key not in st.session_state.board_data:
        if board_type == "スタートからゴール":
            if i == 0:
                st.session_state.board_data[key] = "🚩 START"
            elif i == num_tiles - 1:
                st.session_state.board_data[key] = "🏆 GOAL"
            else:
                st.session_state.board_data[key] = f"マス {i}"
        else:
            st.session_state.board_data[key] = "🔄 循環" if i == num_tiles else f"マス {i+1}"

# サイコロの結果表示
if st.session_state.dice_total > 0:
    render_styled_number("🎲 出目", st.session_state.dice_total)

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
                # 現在地表示
                border_color = '#F44336' if is_curr else '#ccc'
                bg_color = '#FFEB3B' if is_curr else '#f9f9f9'
                label_text = '📍 現在地' if is_curr else f'No. {idx+1}'
                
                st.markdown(f"""
                    <div style='border:3px solid {border_color}; border-radius:10px; padding:5px; text-align:center; background-color:{bg_color}; margin-bottom:5px; color:black;'>
                        <small>{label_text}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                # マス目の名前編集
                st.session_state.board_data[key] = st.text_input(
                    f"t_{idx}", 
                    st.session_state.board_data[key], 
                    key=f"in_{idx}", 
                    label_visibility="collapsed"
                )
                
                if st.button("移動", key=f"b_{idx}", use_container_width=True):
                    st.session_state.current_pos = idx
                    st.rerun()
                
                # 次のマスへの矢印
                if idx < total_tiles - 1:
                    arrow = "👇" if (j + 1) % cols_per_row == 0 else "👉"
                    st.markdown(f"<div style='text-align:center;'>{arrow}</div>", unsafe_allow_html=True)
