import json

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header
from src.utils.time import get_jst_now

# ページの設定
st.set_page_config(page_title="カウントサポートビンゴ", page_icon="🔢", layout="wide")

# グローバルスタイルの適用
render_page_header()

# ビンゴ専用のコンパクトCSS
st.markdown(
    """
    <style>
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        padding: 4px !important;
        gap: 4px !important;
    }
    .st-emotion-cache-16idsys, .st-emotion-cache-1r6slb0 {
        padding: 6px !important;
        margin-bottom: 0px !important;
    }
    .stTextInput input, .stNumberInput input {
        height: 32px !important;
        padding: 2px !important;
        text-align: center !important;
    }
    .stTextInput input {
        font-size: 12px !important;
        opacity: 0.7;
    }
    .stNumberInput input {
        font-size: 20px !important;
        font-weight: 900 !important;
        color: #007bff !important;
    }
    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    input[type=number] {
        -moz-appearance: textfield;
    }
    label { display: none !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; margin-bottom: 5px;'>🔢 カウントサポートビンゴ</h1>", unsafe_allow_html=True
)

# --- ストレージ管理の定義 ---
storage = SafeStorage(LocalStorage())


def get_current_version():
    """
    URLパラメータまたはLocalStorageから現在のデータバージョンを取得します。
    数値として妥当でない場合は "1" を返します。
    """
    v_raw = st.query_params.get("v", None)
    if v_raw:
        # st.query_params の値がリストの場合や文字列の場合があるため安全に処理
        v_str = str(v_raw)
        if v_str.isdigit():
            return v_str

    v_store = storage.get_item("csb_ver", is_json=False)
    if v_store and str(v_store).isdigit():
        return str(v_store)

    return "1"


def get_data_key(version=None):
    v = version if version else get_current_version()
    return f"csb_data_v{v}"


def validate_and_save():
    rows = st.session_state.get("csb_rows", 5)
    cols = st.session_state.get("csb_cols", 5)
    data = {
        "version": get_current_version(),
        "updated_at": get_jst_now().isoformat(),
        "rows": rows,
        "cols": cols,
        "cells": {
            f"{r}_{c}": {
                "label": st.session_state.get(f"csb_label_{r}_{c}", f"項目 {r + 1}-{c + 1}"),
                "count": st.session_state.get(f"csb_count_{r}_{c}", 0),
            }
            for r in range(rows)
            for c in range(cols)
        },
    }
    storage.set_item(get_data_key(), data)
    storage.set_item("csb_ver", get_current_version())


def load_from_storage():
    data = storage.get_item(get_data_key(), is_json=True)
    if not data:
        return False
    try:
        st.session_state.csb_rows, st.session_state.csb_cols = data.get("rows", 5), data.get("cols", 5)
        for pos, cell in data.get("cells", {}).items():
            r, c = pos.split("_")
            st.session_state[f"csb_label_{r}_{c}"] = cell.get("label", "")
            st.session_state[f"csb_count_{r}_{c}"] = cell.get("count", 0)
        return True
    except Exception:
        return False


# 初期化ロジック
if "csb_rows" not in st.session_state:
    if not load_from_storage():
        st.session_state.csb_rows = 5
        st.session_state.csb_cols = 5


def on_change():
    validate_and_save()


# --- メイングリッド ---
current_rows = st.session_state.get("csb_rows", 5)
current_cols = st.session_state.get("csb_cols", 5)

for r in range(current_rows):
    cols_ui = st.columns(current_cols)
    for c in range(current_cols):
        lk, ck = f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"
        if lk not in st.session_state:
            st.session_state[lk] = f"項目 {r + 1}-{c + 1}"
        if ck not in st.session_state:
            st.session_state[ck] = 0
        with cols_ui[c]:
            with st.container(border=True):
                st.text_input(
                    f"L{r}{c}", key=lk, label_visibility="collapsed", on_change=on_change, placeholder="項目名"
                )
                st.number_input(f"N{r}{c}", key=ck, label_visibility="collapsed", step=1, on_change=on_change)

# --- データの保存と読み込み ---
st.write("---")
with st.container(border=True):
    st.subheader("📁 データの保存と読み込み")
    c1, c2 = st.columns(2)
    with c1:
        current_state = {
            "rows": st.session_state.csb_rows,
            "cols": st.session_state.csb_cols,
            "cells": {
                f"{r}_{c}": {
                    "label": st.session_state.get(f"csb_label_{r}_{c}"),
                    "count": st.session_state.get(f"csb_count_{r}_{c}"),
                }
                for r in range(st.session_state.csb_rows)
                for c in range(st.session_state.csb_cols)
            },
        }
        json_str = json.dumps(current_state, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 JSONを保存",
            data=json_str,
            file_name=f"bingo_{get_jst_now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )
    with c2:
        uploaded_file = st.file_uploader("📤 JSONを読み込む", type="json", label_visibility="collapsed")
        if uploaded_file and st.button("反映実行", use_container_width=True):
            try:
                d = json.load(uploaded_file)
                st.session_state.csb_rows, st.session_state.csb_cols = d["rows"], d["cols"]
                for k in list(st.session_state.keys()):
                    if k.startswith("csb_label_") or k.startswith("csb_count_"):
                        del st.session_state[k]
                for pos, cell in d["cells"].items():
                    r, c = pos.split("_")
                    st.session_state[f"csb_label_{r}_{c}"] = cell["label"]
                    st.session_state[f"csb_count_{r}_{c}"] = cell["count"]
                validate_and_save()
                st.rerun()
            except Exception:
                st.error("不正な形式です")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    st.number_input("行数", 1, 15, key="csb_rows", on_change=on_change)
    st.number_input("列数", 1, 15, key="csb_cols", on_change=on_change)
    st.write("---")
    if st.button("🚨 全てリセット", use_container_width=True):
        # LocalStorage 削除
        storage.delete_item(get_data_key())
        # SessionState クリア
        for k in list(st.session_state.keys()):
            if k.startswith("csb_"):
                del st.session_state[k]

        # バージョン更新（安全な変換）
        try:
            current_v = int(get_current_version())
        except (ValueError, TypeError):
            current_v = 1

        new_v = 1 if current_v >= 100 else current_v + 1
        storage.set_item("csb_ver", str(new_v))
        st.query_params["v"] = str(new_v)
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
