import streamlit as st
import random

# ページの設定
st.set_page_config(page_title="今日のおもちゃ", layout="centered")

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

    st.write(f"現在の設定: **{x}d{n}**")

    if st.button("サイコロを振る！", use_container_width=True):
        results = [random.randint(1, n) for _ in range(x)]
        total = sum(results)
        st.write("---")
        st.markdown(f"<h3 style='text-align: center;'>結果</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center;'>{total}</h1>", unsafe_allow_html=True)
        if x > 1:
            st.write(f"出目の内訳: {', '.join(map(str, results))}")
        st.balloons()

elif page == "双六メーカー":
    st.title("🛤️ 双六メーカー")
    st.write("オリジナルの双六盤面を作ってみよう！")

    # 設定エリア
    with st.expander("盤面の設定", expanded=True):
        st.session_state.board_type = st.radio("形式を選択", ["スタートからゴール", "循環型（ループ）"])
        st.session_state.num_tiles = st.slider("マスの数", min_value=3, max_value=50, value=10)

    # 盤面の生成と表示
    st.write("---")
    st.subheader("生成された盤面")

    tiles = []
    num = st.session_state.num_tiles

    if st.session_state.board_type == "スタートからゴール":
        for i in range(num):
            if i == 0:
                tiles.append("🚩 START")
            elif i == num - 1:
                tiles.append("🏆 GOAL")
            else:
                tiles.append(f"マス {i}")
    else:
        for i in range(num):
            tiles.append(f"マス {i+1}")
        tiles.append("🔄 循環")

    # 盤面をグリッドで表示（1行に5マスずつ）
    cols_per_row = 5
    for i in range(0, len(tiles), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(tiles):
                with col:
                    st.markdown(
                        f"""
                        <div style="
                            border: 2px solid #ccc;
                            border-radius: 10px;
                            padding: 15px;
                            text-align: center;
                            background-color: #f9f9f9;
                            margin-bottom: 10px;
                            min-height: 80px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: bold;
                        ">
                            {tiles[i+j]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    # マス間の矢印（最後以外）
                    if i + j < len(tiles) - 1:
                        if (j + 1) % cols_per_row != 0:
                            st.markdown("<div style='text-align: center; font-size: 20px;'>👉</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align: center; font-size: 20px;'>👇</div>", unsafe_allow_html=True)

    st.write("---")
    st.info("この盤面を見ながら、サイコロページで振って遊んでね！")
