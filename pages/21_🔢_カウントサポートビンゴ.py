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
    /* コンテナのパディングを最小限に */
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        padding: 4px !important;
        gap: 4px !important;
    }
    /* 枠付きコンテナの余白調整 */
    .st-emotion-cache-16idsys, .st-emotion-cache-1r6slb0 {
        padding: 6px !important;
        margin-bottom: 0px !important;
    }
    /* 入力フィールドの共通設定 */
    .stTextInput input, .stNumberInput input {
        height: 32px !important;
        padding: 2px !important;
        text-align: center !important;
    }
    /* ラベル用テキスト（小さく） */
    .stTextInput input {
        font-size: 12px !important;
        opacity: 0.7;
    }
    /* 数値用テキスト（大きく太く） */
    .stNumberInput input {
        font-size: 20px !important;
        font-weight: 900 !important;
        color: #007bff !important;
    }
    /* スピンボタン（増減矢印）を隠す（直接入力を優先しつつスペース確保） */
    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    input[type=number] {
        -moz-appearance: textfield;
    }
    /* ラベルの非表示を徹底 */
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
    v_param = st.query_params.get("v", None)
    if v_param:
        return str(v_param)
    v_store = storage.get_item("csb_ver", is_json=False)
    return str(v_store) if v_store else "1"


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


# 初期化
if "csb_ready" not in st.session_state:
    if not load_from_storage():
        st.session_state.csb_rows, st.session_state.csb_cols = 5, 5
    st.session_state.csb_ready = True


def on_change():
    validate_and_save()


# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    rows = st.number_input("行数", 1, 15, key="csb_rows", on_change=on_change)
    cols = st.number_input("列数", 1, 15, key="csb_cols", on_change=on_change)
    st.write("---")
    st.subheader("💾 データ管理")
    current_state = {
        "rows": st.session_state.csb_rows,
        "cols": st.session_state.csb_cols,
        "cells": {
            f"{r}_{c}": {
                "label": st.session_state.get(f"csb_label_{r}_{c}"),
                "count": st.session_state.get(f"csb_count_{r}_{c}"),
            }
            for r in range(rows)
            for c in range(cols)
        },
    }
    json_str = json.dumps(current_state, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 JSON保存",
        data=json_str,
        file_name=f"bingo_{get_jst_now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True,
    )
    uploaded_file = st.file_uploader("📤 JSON読込", type="json")
    if uploaded_file and st.button("復元実行", use_container_width=True):
        try:
            d = json.load(uploaded_file)
            st.session_state.csb_rows, st.session_state.csb_cols = d["rows"], d["cols"]
            for pos, cell in d["cells"].items():
                r, c = pos.split("_")
                st.session_state[f"csb_label_{r}_{c}"] = cell["label"]
                st.session_state[f"csb_count_{r}_{c}"] = cell["count"]
            validate_and_save()
            st.rerun()
        except Exception:
            st.error("不正な形式です")
    st.write("---")
    if st.button("🚨 全てリセット", use_container_width=True):
        storage.delete_item(get_data_key())
        current_v = int(get_current_version())
        new_v = 1 if current_v >= 100 else current_v + 1
        storage.set_item("csb_ver", str(new_v))
        st.query_params["v"] = str(new_v)
        st.rerun()

# --- メイングリッド ---
for r in range(st.session_state.csb_rows):
    cols_ui = st.columns(st.session_state.csb_cols)
    for c in range(st.session_state.csb_cols):
        lk, ck = f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"
        if lk not in st.session_state:
            st.session_state[lk] = f"項目 {r + 1}-{c + 1}"
        if ck not in st.session_state:
            st.session_state[ck] = 0
        with cols_ui[c]:
            with st.container(border=True):
                # テキスト入力（ラベル）
                st.text_input(
                    f"L{r}{c}", key=lk, label_visibility="collapsed", on_change=on_change, placeholder="項目名"
                )
                # 数値入力（カウント）
                st.number_input(f"N{r}{c}", key=ck, label_visibility="collapsed", step=1, on_change=on_change)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
