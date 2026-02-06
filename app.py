import streamlit as st
import random

# ページの設定
st.set_page_config(page_title="今日のおもちゃ", layout="wide")

# セッション状態の初期化
if 'dice_results' not in st.session_state:
    st.session_state.dice_results = []
if 'current_pos' not in st.session_state:
    st.session_state.current_pos = 0
if 'board_data' not in st.session_state:
    st.session_state.board_data = {}

# サイドバーの作成
st.sidebar.title("おもちゃ箱")
page = st.sidebar.selectbox("おもちゃを選んでね", ["ホーム", "サイコロ", "双六メーカー"])

if page == "ホーム":
    st.markdown("<h1 style='text-align: center; margin-top: 10vh;'>今日のおもちゃ</h1>", unsafe_allow_html=True)
    st.write("---")
    st.write("サイドバーからおもちゃを選んで遊んでね！")

elif page == "サイコロ":
    st.title("🎲 サイコロ")
    st.write("ダイスの数(x)と、ダイスの目の数(n)を設定して振ってみよう！")

    col1, col2 = st.columns(2)
    with col1:
        x = st.number_input("ダイスの数 (x)", min_value=1, max_value=100, value=1)
    with col2:
        n = st.number_input("ダイスの目の数 (n)", min_value=1, max_value=1000, value=6)

    if st.button("サイコロを振る！", use_container_width=True):
        results = [random.randint(1, n) for _ in range(x)]
        st.session_state.dice_results = results
        total = sum(results)
        st.write("---")
        st.markdown(f"<h3 style='text-align: center;'>結果</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center;'>{total}</h1>", unsafe_allow_html=True)
        st.balloons()

elif page == "双六メーカー":
    st.title("🛤️ 双六メーカー")
    
    # 設定エリア
    with st.sidebar.expander("盤面の設定", expanded=True):
        board_type = st.radio("形式を選択", ["スタートからゴール", "循環型（ループ）"])
        num_tiles = st.slider("マスの数", min_value=3, max_value=50, value=10)
        if st.button("盤面を初期化"):
            st.session_state.board_data = {}
            st.session_state.current_pos = 0
            st.rerun()

    # データの初期化（不足分を補填）
    total_tiles = num_tiles if board_type == "スタートからゴール" else num_tiles + 1
    for i in range(total_tiles):
        key = f"tile_{i}"
        if key not in st.session_state.board_data:
            if board_type == "スタートからゴール":
                if i == 0: st.session_state.board_data[key] = "🚩 START"
                elif i == num_tiles - 1: st.session_state.board_data[key] = "🏆 GOAL"
                else: st.session_state.board_data[key] = f"マス {i}"
            else:
                if i == num_tiles: st.session_state.board_data[key] = "🔄 循環"
                else: st.session_state.board_data[key] = f"マス {i+1}"

    # 盤面の表示
    st.subheader("双六盤面")
    st.info("マスをクリックして「現在地」を選択できます。テキスト入力で内容も書き換えられます。")

    cols_per_row = 5
    for i in range(0, total_tiles, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < total_tiles:
                key = f"tile_{idx}"
                with col:
                    # 現在地の判定とスタイル設定
                    is_current = (st.session_state.current_pos == idx)
                    bg_color = "#FFEB3B" if is_current else "#f9f9f9"
                    border_color = "#F44336" if is_current else "#ccc"
                    
                    # コンテナ風の表示
                    st.markdown(f"""
                        <div style="
                            border: 3px solid {border_color};
                            border-radius: 10px;
                            padding: 5px;
                            text-align: center;
                            background-color: {bg_color};
                            margin-bottom: 5px;
                            color: black;
                        ">
                            <small>{"📍 現在地" if is_current else f"No. {idx+1}"}</small>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # テキスト編集
                    st.session_state.board_data[key] = st.text_input(
                        f"text_{idx}", 
                        value=st.session_state.board_data[key],
                        key=f"input_{idx}",
                        label_visibility="collapsed"
                    )
                    
                    # 現在地に設定ボタン
                    if st.button("ここへ移動", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.current_pos = idx
                        st.rerun()
                        
                    if idx < total_tiles - 1:
                        st.markdown("<div style='text-align: center;'>👇</div>" if (j+1)%cols_per_row==0 else "<div style='text-align: center;'>👉</div>", unsafe_allow_html=True)

    st.write("---")
    st.write(f"現在の位置: **No. {st.session_state.current_pos + 1} ({st.session_state.board_data[f'tile_{st.session_state.current_pos}']})**")