import streamlit as st
import random

# ページの設定
st.set_page_config(page_title="今日のおもちゃ", layout="centered")

# サイドバーの作成
st.sidebar.title("おもちゃ箱")
page = st.sidebar.selectbox("おもちゃを選んでね", ["ホーム", "サイコロ"])

if page == "ホーム":
    # 中央にテキストを表示
    st.markdown("<h1 style='text-align: center; margin-top: 10vh;'>今日のおもちゃ</h1>", unsafe_allow_html=True)
    st.write("---")
    st.write("サイドバーからおもちゃを選んで遊んでね！")

elif page == "サイコロ":
    st.title("🎲 サイコロ")
    st.write("ダイスの数(x)と、ダイスの目の数(n)を設定して振ってみよう！")

    # 入力設定
    col1, col2 = st.columns(2)
    with col1:
        x = st.number_input("ダイスの数 (x)", min_value=1, max_value=100, value=1)
    with col2:
        n = st.number_input("ダイスの目の数 (n)", min_value=1, max_value=1000, value=6)

    st.write(f"現在の設定: **{x}d{n}**")

    # サイコロを振るボタン
    if st.button("サイコロを振る！", use_container_width=True):
        results = [random.randint(1, n) for _ in range(x)]
        total = sum(results)
        
        st.write("---")
        st.markdown(f"<h3 style='text-align: center;'>結果</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center;'>{total}</h1>", unsafe_allow_html=True)
        
        if x > 1:
            st.write(f"出目の内訳: {', '.join(map(str, results))}")
        
        # 演出用の絵文字
        st.balloons()