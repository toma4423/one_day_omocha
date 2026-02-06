import streamlit as st

st.set_page_config(page_title="カウントサポート", page_icon="🔢")

if 'cs_reset_counter' not in st.session_state:
    st.session_state.cs_reset_counter = 0

def init_cs_state():
    if 'cs_x' not in st.session_state: st.session_state.cs_x = 0
    if 'cs_y' not in st.session_state: st.session_state.cs_y = 0
    if 'cs_z' not in st.session_state: st.session_state.cs_z = 0
    if 'cs_weight_x' not in st.session_state: st.session_state.cs_weight_x = 1.0
    if 'cs_weight_y' not in st.session_state: st.session_state.cs_weight_y = 1.0
    if 'cs_weight_z' not in st.session_state: st.session_state.cs_weight_z = 1.0

init_cs_state()

# カウントサポート用UI
def weighted_counter_ui(label, key_val, key_weight):
    st.markdown(f"#### {label}")
    col_val, col_w = st.columns([2, 1])
    
    # リセットカウンターをキーに含めることで、リセット時にウィジェットを強制再生成させる
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
    # セッション状態の値を初期化
    st.session_state.cs_x = 0
    st.session_state.cs_y = 0
    st.session_state.cs_z = 0
    st.session_state.cs_weight_x = 1.0
    st.session_state.cs_weight_y = 1.0
    st.session_state.cs_weight_z = 1.0
    
    # キーをリセットすることでウィジェットを再生成させる
    st.session_state.cs_reset_counter += 1
    st.rerun()
