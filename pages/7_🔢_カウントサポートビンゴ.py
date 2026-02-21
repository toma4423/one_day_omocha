import streamlit as st
import json
from datetime import datetime
from src.utils.time import get_jst_now
from streamlit_local_storage import LocalStorage
from src.utils.storage import SafeStorage

# ページの設定
st.set_page_config(page_title="カウントサポートビンゴ", page_icon="🔢", layout="wide")

# スマホ対応用のカスタムCSS
st.markdown("""
    <style>
    .stButton > button {
        height: 60px !important;
        font-size: 24px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }
    .stNumberInput input {
        font-size: 20px !important;
        text-align: center !important;
        height: 50px !important;
    }
    .stTextInput input {
        font-size: 16px !important;
        text-align: center !important;
    }
    @media (max_width: 600px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔢 カウントサポートビンゴ")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# --- バージョン管理とキーの定義 ---
# ストレージの競合を防ぐためのバージョンキー
VERSION_KEY = "csb_storage_ver"

def get_storage_version():
    """現在のストレージバージョンを取得します。"""
    v = storage.get_item(VERSION_KEY)
    try:
        return int(v) if v is not None else 1
    except (ValueError, TypeError):
        return 1

def get_grid_data_key():
    """バージョンを含めたデータキーを返します。"""
    v = get_storage_version()
    return f"csb_grid_data_v{v}"

def save_grid_to_storage():
    """現在のグリッド状態を、現在のバージョンキーで保存します。"""
    data = {
        "rows": st.session_state.csb_rows,
        "cols": st.session_state.csb_cols,
        "cells": {}
    }
    for r in range(st.session_state.csb_rows):
        for c in range(st.session_state.csb_cols):
            lk, ck = f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"
            data["cells"][f"{r}_{c}"] = {
                "label": st.session_state.get(lk, f"項目 {r+1}-{c+1}"),
                "count": st.session_state.get(ck, 0)
            }
    storage.set_item(get_grid_data_key(), data)

def load_grid_from_storage():
    """現在のバージョンのデータを LocalStorage から復元します。"""
    key = get_grid_data_key()
    data = storage.get_item(key, is_json=True)
    if not data:
        return False
    
    st.session_state.csb_rows = data.get("rows", 5)
    st.session_state.csb_cols = data.get("cols", 5)
    cells = data.get("cells", {})
    
    for pos, cell_data in cells.items():
        r, c = pos.split("_")
        st.session_state[f"csb_label_{r}_{c}"] = str(cell_data.get("label", ""))
        st.session_state[f"csb_count_{r}_{c}"] = int(cell_data.get("count", 0))
    return True

# --- 初期化 ---
if "csb_initialized" not in st.session_state:
    if not load_grid_from_storage():
        st.session_state.csb_rows = 5
        st.session_state.csb_cols = 5
    st.session_state.csb_initialized = True

def init_cell_state(r, c):
    lk, ck = f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"
    if lk not in st.session_state:
        st.session_state[lk] = f"項目 {r+1}-{c+1}"
    if ck not in st.session_state:
        st.session_state[ck] = 0
    return lk, ck

def on_val_change():
    save_grid_to_storage()

def on_plus(key):
    st.session_state[key] += 1
    save_grid_to_storage()

def on_minus(key):
    st.session_state[key] -= 1
    save_grid_to_storage()

# サイドバーの設定項目
with st.sidebar:
    st.header("設定")
    rows = st.number_input("行数", min_value=1, max_value=15, key="csb_rows", on_change=on_val_change)
    cols_num = st.number_input("列数", min_value=1, max_value=15, key="csb_cols", on_change=on_val_change)
    
    st.write("---")
    st.subheader("💾 セーブ & ロード")
    
    # JSONセーブ
    save_data = {
        "rows": st.session_state.csb_rows,
        "cols": st.session_state.csb_cols,
        "cells": {}
    }
    for r in range(rows):
        for c in range(cols_num):
            lk, ck = init_cell_state(r, c)
            save_data["cells"][f"{r}_{c}"] = {"label": st.session_state[lk], "count": st.session_state[ck]}
    
    json_str = json.dumps(save_data, indent=2, ensure_ascii=False)
    timestamp = get_jst_now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="JSONをダウンロード",
        data=json_str,
        file_name=f"bingo_save_{timestamp}.json",
        mime="application/json",
        use_container_width=True
    )

    # JSONロード
    uploaded_file = st.file_uploader("JSONをアップロード", type="json")
    if uploaded_file is not None:
        if st.button("復元する", use_container_width=True):
            try:
                data_load = json.load(uploaded_file)
                st.session_state.csb_rows = data_load.get("rows", 5)
                st.session_state.csb_cols = data_load.get("cols", 5)
                
                # 古いセルの状態をクリア
                for key in list(st.session_state.keys()):
                    if key.startswith("csb_label_") or key.startswith("csb_count_"):
                        del st.session_state[key]

                cells = data_load.get("cells", {})
                for pos, cell_data in cells.items():
                    r, c = pos.split("_")
                    st.session_state[f"csb_label_{r}_{c}"] = str(cell_data.get("label", ""))
                    st.session_state[f"csb_count_{r}_{c}"] = int(cell_data.get("count", 0))
                
                save_grid_to_storage()
                st.success("復元しました！")
                st.rerun()
            except Exception:
                st.error("JSONの読み込みに失敗しました")

    st.write("---")
    # リセットボタン（バージョンを上げることで確実かつ一瞬で初期化する）
    if st.button("全てをリセット", use_container_width=True):
        # 1. 現在のデータキーを削除（ゴミ掃除）
        storage.delete_item(get_grid_data_key())
        
        # 2. バージョンを上げる（これにより古いデータは一切読み込まれなくなる）
        new_ver = get_storage_version() + 1
        storage.set_item(VERSION_KEY, new_ver)
        
        # 3. セッション状態をクリア
        for key in list(st.session_state.keys()):
            if key.startswith("csb_"):
                del st.session_state[key]
        
        st.success(f"リセット完了 (Ver.{new_ver})")
        st.rerun()

    st.info("自動保存：ブラウザ（LocalStorage）")

# メイングリッド表示
for r in range(rows):
    cols = st.columns(cols_num)
    for c in range(cols_num):
        label_key, count_key = init_cell_state(r, c)
        with cols[c]:
            st.text_input(f"L_{r}_{c}", key=label_key, label_visibility="collapsed", on_change=on_val_change)
            
            c_m, c_v, c_p = st.columns([1, 1.5, 1])
            with c_m:
                st.button("－", key=f"btn_m_{r}_{c}", use_container_width=True, on_click=on_minus, args=(count_key,))
            with c_v:
                st.number_input(f"N_{r}_{c}", key=count_key, label_visibility="collapsed", step=1, on_change=on_val_change)
            with c_p:
                st.button("＋", key=f"btn_p_{r}_{c}", use_container_width=True, on_click=on_plus, args=(count_key,))
