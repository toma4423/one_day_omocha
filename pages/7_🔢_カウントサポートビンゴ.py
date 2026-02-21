import streamlit as st
import pandas as pd
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

# --- データ構造の定義 ---
# グリッド全体を一つの JSON として管理するためのキー
GRID_DATA_KEY = "csb_grid_data"

def save_grid_to_storage():
    """現在のグリッド状態を一つの JSON として保存します。"""
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
    storage.set_item(GRID_DATA_KEY, data)

def load_grid_from_storage():
    """LocalStorage からグリッド全体を復元します。"""
    data = storage.get_item(GRID_DATA_KEY, is_json=True)
    if not data:
        return False
    
    st.session_state.csb_rows = data.get("rows", 5)
    st.session_state.csb_cols = data.get("cols", 5)
    cells = data.get("cells", {})
    
    for pos, cell_data in cells.items():
        r, c = pos.split("_")
        st.session_state[f"csb_label_{r}_{c}"] = cell_data.get("label", f"項目 {int(r)+1}-{int(c)+1}")
        st.session_state[f"csb_count_{r}_{c}"] = cell_data.get("count", 0)
    return True

# --- 初期化 ---
if GRID_DATA_KEY not in st.session_state:
    # ページ読み込み時に一度だけロードを試みる
    if not load_grid_from_storage():
        # データがなければデフォルト
        st.session_state.csb_rows = 5
        st.session_state.csb_cols = 5
    st.session_state[GRID_DATA_KEY] = True # ロード完了フラグ

# セッション状態の初期化（各セル用）
def init_cell_state(r, c):
    lk, ck = f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"
    if lk not in st.session_state:
        st.session_state[lk] = f"項目 {r+1}-{c+1}"
    if ck not in st.session_state:
        st.session_state[ck] = 0
    return lk, ck

# コールバック関数
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
    
    # CSVダウンロード
    save_data_list = []
    for r in range(rows):
        for c in range(cols_num):
            lk, ck = init_cell_state(r, c)
            save_data_list.append({"row": r, "col": c, "label": st.session_state[lk], "count": st.session_state[ck]})
    
    df_save = pd.DataFrame(save_data_list)
    csv_data = df_save.to_csv(index=False).encode('utf-8')
    timestamp = get_jst_now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="CSVをダウンロード",
        data=csv_data,
        file_name=f"bingo_save_{timestamp}.csv",
        mime="text/csv",
        use_container_width=True
    )

    # CSVロード
    uploaded_file = st.file_uploader("CSVをアップロード", type="csv")
    if uploaded_file is not None:
        if st.button("復元する", use_container_width=True):
            try:
                df_load = pd.read_csv(uploaded_file)
                st.session_state.csb_rows = int(df_load['row'].max()) + 1
                st.session_state.csb_cols = int(df_load['col'].max()) + 1
                for _, row_data in df_load.iterrows():
                    r, c = int(row_data['row']), int(row_data['col'])
                    st.session_state[f"csb_label_{r}_{c}"] = str(row_data['label'])
                    st.session_state[f"csb_count_{r}_{c}"] = int(row_data['count'])
                save_grid_to_storage() # JSON に保存
                st.success("復元しました！")
                st.rerun()
            except Exception:
                st.error("ロードに失敗しました")

    st.write("---")
    # リセットボタン（JSONキーを消すだけなので確実かつゴミが出ない）
    if st.button("全てをリセット", use_container_width=True):
        # セッションの csb_ キーをすべて削除
        storage.clear_all_with_prefix("csb_")
        # JSON オブジェクトを削除
        storage.delete_item(GRID_DATA_KEY)
        st.success("リセット完了")
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
