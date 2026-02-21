import streamlit as st
import json
from src.utils.styles import render_result_box
from src.utils.time import get_jst_now
from streamlit_local_storage import LocalStorage
from src.utils.storage import SafeStorage

st.set_page_config(page_title="カウントサポート", page_icon="🔢")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())
CS_STORAGE_KEY = "cs_data"

# セッション状態の初期化
if 'cs_reset_counter' not in st.session_state:
    st.session_state.cs_reset_counter = 0

def save_to_storage():
    """現在の状態を LocalStorage に保存します。"""
    data = {
        'x': st.session_state.get('cs_x', 0),
        'y': st.session_state.get('cs_y', 0),
        'z': st.session_state.get('cs_z', 0),
        'weight_x': st.session_state.get('cs_weight_x', 1.0),
        'weight_y': st.session_state.get('cs_weight_y', 1.0),
        'weight_z': st.session_state.get('cs_weight_z', 1.0)
    }
    storage.set_item(CS_STORAGE_KEY, data)

def load_from_storage():
    """LocalStorage から状態を復元します。"""
    data = storage.get_item(CS_STORAGE_KEY, is_json=True)
    if data:
        st.session_state.cs_x = data.get('x', 0)
        st.session_state.cs_y = data.get('y', 0)
        st.session_state.cs_z = data.get('z', 0)
        st.session_state.cs_weight_x = data.get('weight_x', 1.0)
        st.session_state.cs_weight_y = data.get('weight_y', 1.0)
        st.session_state.cs_weight_z = data.get('weight_z', 1.0)
        return True
    return False

def init_cs_state():
    if 'cs_x' not in st.session_state:
        if not load_from_storage():
            st.session_state.cs_x = 0
            st.session_state.cs_y = 0
            st.session_state.cs_z = 0
            st.session_state.cs_weight_x = 1.0
            st.session_state.cs_weight_y = 1.0
            st.session_state.cs_weight_z = 1.0

init_cs_state()

def weighted_counter_ui(label: str, key_val: str, key_weight: str):
    """
    重み付きカウンターのUIを表示し、算出値を返します。
    """
    st.markdown(f"#### {label}")
    col_val, col_w = st.columns([2, 1])
    
    reset_id = st.session_state.cs_reset_counter
    
    with col_val:
        # 入力時に自動保存を走らせるため on_change を追加
        st.session_state[key_val] = st.number_input(
            f"{label}の数", 
            value=st.session_state[key_val], 
            key=f"w_{key_val}_{reset_id}",
            on_change=save_to_storage
        )
    with col_w:
        st.session_state[key_weight] = st.number_input(
            f"{label}の倍率", 
            value=st.session_state[key_weight], 
            key=f"w_{key_weight}_{reset_id}", 
            step=0.1,
            on_change=save_to_storage
        )
    
    current_weighted = st.session_state[key_val] * st.session_state[key_weight]
    st.caption(f"現在の{label}値: {current_weighted:.1f}")
    return current_weighted

st.title("🔢 カウントサポート")

# --- サイドバー：セーブ＆ロード ---
with st.sidebar:
    st.header("💾 セーブ & ロード")
    
    # JSONセーブ
    current_data = {
        'x': st.session_state.cs_x, 'y': st.session_state.cs_y, 'z': st.session_state.cs_z,
        'weight_x': st.session_state.cs_weight_x, 'weight_y': st.session_state.cs_weight_y, 'weight_z': st.session_state.cs_weight_z
    }
    json_str = json.dumps(current_data, indent=2)
    timestamp = get_jst_now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="JSONをダウンロード",
        data=json_str,
        file_name=f"count_support_{timestamp}.json",
        mime="application/json",
        use_container_width=True
    )

    # JSONロード
    uploaded_file = st.file_uploader("JSONをアップロード", type="json")
    if uploaded_file is not None:
        if st.button("復元する", use_container_width=True):
            try:
                data_load = json.load(uploaded_file)
                st.session_state.cs_x = data_load.get('x', 0)
                st.session_state.cs_y = data_load.get('y', 0)
                st.session_state.cs_z = data_load.get('z', 0)
                st.session_state.cs_weight_x = data_load.get('weight_x', 1.0)
                st.session_state.cs_weight_y = data_load.get('weight_y', 1.0)
                st.session_state.cs_weight_z = data_load.get('weight_z', 1.0)
                save_to_storage()
                st.success("復元しました！")
                st.rerun()
            except Exception:
                st.error("JSONの読み込みに失敗しました")

    st.write("---")
    if st.button("全ての数値をリセット", use_container_width=True):
        st.session_state.cs_x = 0
        st.session_state.cs_y = 0
        st.session_state.cs_z = 0
        st.session_state.cs_weight_x = 1.0
        st.session_state.cs_weight_y = 1.0
        st.session_state.cs_weight_z = 1.0
        st.session_state.cs_reset_counter += 1
        storage.delete_item(CS_STORAGE_KEY)
        st.rerun()

# --- メインエリア ---
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
