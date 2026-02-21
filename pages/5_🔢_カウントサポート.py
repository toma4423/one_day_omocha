import streamlit as st
from src.utils.styles import render_result_box, render_donation_box

st.set_page_config(page_title="カウントサポート", page_icon="🔢")

# 募金箱設置
PAYPAY_URL = "https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s"
render_donation_box(PAYPAY_URL)

# セッション状態の初期化
if 'cs_reset_counter' not in st.session_state:
    st.session_state.cs_reset_counter = 0

def init_cs_state():
    defaults = {
        'cs_x': 0, 'cs_y': 0, 'cs_z': 0,
        'cs_weight_x': 1.0, 'cs_weight_y': 1.0, 'cs_weight_z': 1.0
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_cs_state()

def weighted_counter_ui(label: str, key_val: str, key_weight: str):
    """
    重み付きカウンターのUIを表示し、算出値を返します。
    """
    st.markdown(f"#### {label}")
    col_val, col_w = st.columns([2, 1])
    
    # リセット用ID
    reset_id = st.session_state.cs_reset_counter
    
    with col_val:
        st.session_state[key_val] = st.number_input(
            f"{label}の数", 
            value=st.session_state[key_val], 
            key=f"w_{key_val}_{reset_id}"
        )
    with col_w:
        st.session_state[key_weight] = st.number_input(
            f"{label}の倍率", 
            value=st.session_state[key_weight], 
            key=f"w_{key_weight}_{reset_id}", 
            step=0.1
        )
    
    current_weighted = st.session_state[key_val] * st.session_state[key_weight]
    st.caption(f"現在の{label}値: {current_weighted:.1f}")
    return current_weighted

st.title("🔢 カウントサポート")

col_main1, col_space, col_main2 = st.columns([2, 0.5, 2])

with col_main1:
    st.subheader("基本カウント")
    val_x = weighted_counter_ui("X", "cs_x", "cs_weight_x")
    val_y = weighted_counter_ui("Y", "cs_y", "cs_weight_y")
    
    st.write("---")
    render_result_box("X - Y (算出値)", f"{val_x - val_y:.1f}")

with col_main2:
    st.subheader("追加カウント")
    val_z = weighted_counter_ui("Z", "cs_z", "cs_weight_z")
    
    st.write("---")
    diff_xy = val_x - val_y
    render_result_box("(X - Y) - Z", f"{diff_xy - val_z:.1f}", bg_color="#E8F5E9", border_color="#2E7D32", text_color="#2E7D32", font_size=64)

if st.sidebar.button("全ての数値をリセット"):
    st.session_state.cs_x = 0
    st.session_state.cs_y = 0
    st.session_state.cs_z = 0
    st.session_state.cs_weight_x = 1.0
    st.session_state.cs_weight_y = 1.0
    st.session_state.cs_weight_z = 1.0
    st.session_state.cs_reset_counter += 1
    st.rerun()
