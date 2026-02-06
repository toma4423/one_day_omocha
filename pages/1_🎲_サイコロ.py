import streamlit as st
import random

st.set_page_config(page_title="サイコロ", page_icon="🎲")

st.title("🎲 サイコロ")
col1, col2 = st.columns(2)
with col1: x = st.number_input("ダイスの数 (x)", 1, 100, 1)
with col2: n = st.number_input("ダイスの目の数 (n)", 1, 1000, 6)
if st.button("サイコロを振る！", use_container_width=True):
    total = sum([random.randint(1, n) for _ in range(x)])
    st.write("---")
    st.markdown(f"<h3 style='text-align: center;'>結果</h3><h1 style='text-align: center;'>{total}</h1>", unsafe_allow_html=True)
    st.balloons()
