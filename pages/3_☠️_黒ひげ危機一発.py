import streamlit as st
import random

st.set_page_config(page_title="黒ひげ危機一発", page_icon="☠️")

if 'kurohige_status' not in st.session_state: st.session_state.kurohige_status = "ready"

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
