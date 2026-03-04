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

# 外部CSSの読み込み
try:
    with open("src/assets/counter/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# ビンゴ専用の微調整CSS
st.markdown(
    """
    <style>
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        padding: 2px !important;
        gap: 2px !important;
    }
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label {
        display: none !important;
    }
    .stNumberInput input {
        font-size: 22px !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    /* リセット時のフェードアウトアニメーション */
    .resetting {
        transition: opacity 0.5s ease;
        opacity: 0 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; margin-bottom: 10px;'>🔢 カウントサポートビンゴ</h1>", unsafe_allow_html=True
)

# --- ストレージ管理の定義 ---
storage = SafeStorage(LocalStorage())

def get_current_version():
    v_raw = st.query_params.get("v", None)
    if v_raw:
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

if "csb_rows" not in st.session_state:
    if not load_from_storage():
        st.session_state.csb_rows = 5
        st.session_state.csb_cols = 5

def on_change():
    validate_and_save()

# --- クエリパラメータによるJSリセット命令の受信 ---
if "reset_action" in st.query_params:
    action = st.query_params["reset_action"]
    if action == "count_only":
        for k in st.session_state.keys():
            if k.startswith("csb_count_"):
                st.session_state[k] = 0
        validate_and_save()
    elif action == "all":
        storage.delete_item(get_data_key())
        for k in list(st.session_state.keys()):
            if k.startswith("csb_"): del st.session_state[k]
        try:
            current_v = int(get_current_version())
        except (ValueError, TypeError):
            current_v = 1
        new_v = 1 if current_v >= 100 else current_v + 1
        storage.set_item("csb_ver", str(new_v))
        st.query_params["v"] = str(new_v)
    
    # 処理が終わったらクエリパラメータを消してリロード
    del st.query_params["reset_action"]
    st.rerun()

# --- メイングリッド ---
current_rows = st.session_state.get("csb_rows", 5)
current_cols = st.session_state.get("csb_cols", 5)
bingo_matrix = []

for r in range(current_rows):
    cols_ui = st.columns(current_cols)
    row_data = []
    for c in range(current_cols):
        lk, ck = f"csb_label_{r}_{c}", f"csb_count_{r}_{c}"
        if lk not in st.session_state: st.session_state[lk] = f"項目 {r + 1}-{c + 1}"
        if ck not in st.session_state: st.session_state[ck] = 0
        
        count_val = st.session_state[ck]
        is_active = count_val > 0
        row_data.append(is_active)
        
        with cols_ui[c]:
            cell_class = "bingo-cell-active" if is_active else ""
            with st.container(border=True):
                st.markdown(f"<div id='cell-{r}-{c}' class='{cell_class}'>", unsafe_allow_html=True)
                st.text_input(f"L{r}{c}", key=lk, label_visibility="collapsed", on_change=on_change, placeholder="項目名")
                st.number_input(f"N{r}{c}", key=ck, label_visibility="collapsed", step=1, on_change=on_change)
                st.markdown("</div>", unsafe_allow_html=True)
    bingo_matrix.append(row_data)

# --- ビンゴ判定ロジック ---
bingo_indices = []
for r in range(current_rows):
    if all(bingo_matrix[r]): bingo_indices.extend([[r, c] for c in range(current_cols)])
for c in range(current_cols):
    if all(bingo_matrix[r][c] for r in range(current_rows)): bingo_indices.extend([[r, c] for r in range(current_rows)])
if current_rows == current_cols:
    if all(bingo_matrix[i][i] for i in range(current_rows)): bingo_indices.extend([[i, i] for i in range(current_rows)])
    if all(bingo_matrix[i][current_cols - 1 - i] for i in range(current_rows)): bingo_indices.extend([[i, current_cols - 1 - i] for i in range(current_rows)])

if bingo_indices:
    unique_indices = []
    for pair in bingo_indices:
        if pair not in unique_indices: unique_indices.append(pair)
    js_highlight = "".join([f"document.getElementById('cell-{r}-{c}').parentElement.parentElement.parentElement.classList.add('bingo-line-complete');" for r, c in unique_indices])
    st.components.v1.html(f"<script>{js_highlight}</script>", height=0)
    st.balloons()

# --- データの保存と読み込み ---
st.write("---")
with st.container(border=True):
    st.subheader("📁 データの保存と読み込み")
    c1, c2 = st.columns(2)
    with c1:
        current_state = {
            "rows": st.session_state.csb_rows,
            "cols": st.session_state.csb_cols,
            "cells": {f"{r}_{c}": {"label": st.session_state.get(f"csb_label_{r}_{c}"), "count": st.session_state.get(f"csb_count_{r}_{c}")} for r in range(st.session_state.csb_rows) for c in range(st.session_state.csb_cols)},
        }
        json_str = json.dumps(current_state, indent=2, ensure_ascii=False)
        st.download_button(label="📥 現在の設定をJSONで保存", data=json_str, file_name=f"bingo_{get_jst_now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)
    with c2:
        uploaded_file = st.file_uploader("📤 JSONを読み込んで復元", type="json", label_visibility="collapsed")
        if uploaded_file and st.button("反映実行", use_container_width=True, type="primary"):
            try:
                d = json.load(uploaded_file)
                st.session_state.csb_rows, st.session_state.csb_cols = d["rows"], d["cols"]
                for k in list(st.session_state.keys()):
                    if k.startswith("csb_label_") or k.startswith("csb_count_"): del st.session_state[k]
                for pos, cell in d["cells"].items():
                    r, c = pos.split("_")
                    st.session_state[f"csb_label_{r}_{c}"] = cell["label"]
                    st.session_state[f"csb_count_{r}_{c}"] = cell["count"]
                validate_and_save()
                st.rerun()
            except Exception: st.error("不正な形式です")

# --- サイドバー (JSリセット実装) ---
with st.sidebar:
    st.header("⚙️ 設定")
    st.number_input("行数", 1, 15, key="csb_rows", on_change=on_change)
    st.number_input("列数", 1, 15, key="csb_cols", on_change=on_change)
    st.write("---")
    
    # JavaScriptを用いたリセットボタン
    st.subheader("🚨 リセット")
    
    # 1. カウントのみリセット (JS確認付き)
    if st.button("🔢 カウントのみ0にする", use_container_width=True):
        js_confirm = """
        <script>
        if (window.confirm('全てのカウントを0に戻しますか？（項目名は残ります）')) {
            const url = new URL(window.parent.location.href);
            url.searchParams.set('reset_action', 'count_only');
            window.parent.location.href = url.href;
        }
        </script>
        """
        st.components.v1.html(js_confirm, height=0)

    # 2. 全てリセット (JS確認付き)
    if st.button("🚨 全てリセット", use_container_width=True, type="secondary", help="項目名も含めて完全に初期化します"):
        js_confirm_all = """
        <script>
        if (window.confirm('項目名も含めて、全てのデータを完全に消去しますか？')) {
            const url = new URL(window.parent.location.href);
            url.searchParams.set('reset_action', 'all');
            window.parent.location.href = url.href;
        }
        </script>
        """
        st.components.v1.html(js_confirm_all, height=0)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
