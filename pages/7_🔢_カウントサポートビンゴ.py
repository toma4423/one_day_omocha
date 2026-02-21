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
    .stButton > button { height: 60px !important; font-size: 20px !important; border-radius: 12px !important; }
    .stNumberInput input { font-size: 18px !important; text-align: center !important; }
    .stTextInput input { font-size: 16px !important; text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔢 カウントサポートビンゴ")

# --- ストレージ管理の定義 ---
storage = SafeStorage(LocalStorage())

def get_current_version():
    """URLまたはストレージから現在のデータバージョンを取得します。"""
    # 1. URLパラメータを優先
    v_param = st.query_params.get("v", None)
    if v_param:
        return str(v_param)
    # 2. ストレージから取得
    v_store = storage.get_item("csb_ver", is_json=False)
    return str(v_store) if v_store else "1"

def get_data_key():
    """バージョンに基づいた一意のデータキーを生成します。"""
    return f"csb_data_v{get_current_version()}"

def validate_and_save():
    """現在の状態を検証して JSON 保存します。"""
    rows = st.session_state.get("csb_rows", 5)
    cols = st.session_state.get("csb_cols", 5)
    
    data = {
        "version": get_current_version(),
        "updated_at": get_jst_now().isoformat(),
        "rows": rows,
        "cols": cols,
        "cells": {}
    }
    
    for r in range(rows):
        for c in range(cols):
            lk, ck = f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"
            data["cells"][f"{r}_{c}"] = {
                "label": st.session_state.get(lk, f"項目 {r+1}-{c+1}"),
                "count": st.session_state.get(ck, 0)
            }
    
    storage.set_item(get_data_key(), data)
    storage.set_item("csb_ver", get_current_version())

def load_from_storage():
    """ストレージからデータを復元します。"""
    key = get_data_key()
    data = storage.get_item(key, is_json=True)
    
    if not data:
        return False
    
    try:
        st.session_state.csb_rows = data.get("rows", 5)
        st.session_state.csb_cols = data.get("cols", 5)
        cells = data.get("cells", {})
        for pos, cell in cells.items():
            r, c = pos.split("_")
            st.session_state[f"csb_label_{r}_{c}"] = cell.get("label", "")
            st.session_state[f"csb_count_{r}_{c}"] = cell.get("count", 0)
        return True
    except Exception:
        return False

# --- 初期化 ---
if "csb_ready" not in st.session_state:
    if not load_from_storage():
        st.session_state.csb_rows = 5
        st.session_state.csb_cols = 5
    st.session_state.csb_ready = True

# 各セルのキー管理
def get_keys(r, c):
    return f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"

# コールバック
def on_change():
    validate_and_save()

def on_step(key, delta):
    st.session_state[key] += delta
    validate_and_save()

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    rows = st.number_input("行数", 1, 15, key="csb_rows", on_change=on_change)
    cols = st.number_input("列数", 1, 15, key="csb_cols", on_change=on_change)
    
    st.write("---")
    st.subheader("💾 セーブ & ロード")
    
    # セーブデータの検証と作成
    current_state = {
        "rows": st.session_state.csb_rows,
        "cols": st.session_state.csb_cols,
        "cells": {f"{r}_{c}": {"label": st.session_state.get(f"csb_label_{r}_{c}"), "count": st.session_state.get(f"csb_count_{r}_{c}")} for r in range(rows) for c in range(cols)}
    }
    
    json_str = json.dumps(current_state, indent=2, ensure_ascii=False)
    st.download_button(
        label="JSONを保存",
        data=json_str,
        file_name=f"bingo_{get_jst_now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
        use_container_width=True
    )

    uploaded_file = st.file_uploader("JSONを読込", type="json")
    if uploaded_file and st.button("復元実行", use_container_width=True):
        try:
            d = json.load(uploaded_file)
            st.session_state.csb_rows, st.session_state.csb_cols = d["rows"], d["cols"]
            # セッションクリア
            for k in list(st.session_state.keys()):
                if k.startswith("csb_label_") or k.startswith("csb_count_"): del st.session_state[k]
            # データ流し込み
            for pos, cell in d["cells"].items():
                r, c = pos.split("_")
                st.session_state[f"csb_label_{r}_{c}"], st.session_state[f"csb_count_{r}_{c}"] = cell["label"], cell["count"]
            validate_and_save()
            st.success("復元完了")
            st.rerun()
        except Exception:
            st.error("不正な形式です")

    st.write("---")
    if st.button("🚨 全てをリセット", use_container_width=True):
        # バージョンを更新してURLパラメータにセット
        new_v = str(int(get_current_version()) + 1)
        st.query_params["v"] = new_v
        storage.set_item("csb_ver", new_v)
        # 内部状態クリア
        for k in list(st.session_state.keys()):
            if k.startswith("csb_"): del st.session_state[k]
        st.success("リセットしました (リロード中...)")
        st.rerun()

# --- メイングリッド ---
for r in range(st.session_state.csb_rows):
    cols_ui = st.columns(st.session_state.csb_cols)
    for c in range(st.session_state.csb_cols):
        lk, ck = get_keys(r, c)
        if lk not in st.session_state: st.session_state[lk] = f"項目 {r+1}-{c+1}"
        if ck not in st.session_state: st.session_state[ck] = 0
        
        with cols_ui[c]:
            st.text_input(f"L{r}{c}", key=lk, label_visibility="collapsed", on_change=on_change)
            c_m, c_v, c_p = st.columns([1, 1.5, 1])
            with c_m: st.button("－", key=f"m{r}{c}", use_container_width=True, on_click=on_step, args=(ck, -1))
            with c_v: st.number_input(f"N{r}{c}", key=ck, label_visibility="collapsed", step=1, on_change=on_change)
            with c_p: st.button("＋", key=f"p{r}{c}", use_container_width=True, on_click=on_step, args=(ck, 1))
