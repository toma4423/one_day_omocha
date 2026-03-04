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

# ビンゴ専用「超コンパクト」CSS
st.markdown(
    """
    <style>
    .main .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    h1 { margin-top: -30px !important; margin-bottom: 0px !important; font-size: 1.8rem !important; }
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] { padding: 0px !important; gap: 2px !important; }
    div[data-testid="stElementContainer"] div.st-emotion-cache-16idsys, 
    div[data-testid="stElementContainer"] div.st-emotion-cache-1r6slb0 { padding: 4px !important; margin: 0px !important; }
    .stTextInput input { height: 24px !important; font-size: 11px !important; padding: 0 4px !important; margin-bottom: 2px !important; }
    .stNumberInput input { height: 32px !important; font-size: 20px !important; font-weight: 900 !important; padding: 0 !important; }
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label { display: none !important; }
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    hr { margin: 0.5rem 0 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center;'>🔢 カウントサポートビンゴ</h1>", unsafe_allow_html=True)

storage = SafeStorage(LocalStorage())

def get_current_version():
    v_raw = st.query_params.get("v", "1")
    return str(v_raw)

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
    if not data: return False
    try:
        st.session_state.csb_rows, st.session_state.csb_cols = data.get("rows", 5), data.get("cols", 5)
        for pos, cell in data.get("cells", {}).items():
            r, c = pos.split("_")
            st.session_state[f"csb_label_{r}_{c}"] = cell.get("label", "")
            st.session_state[f"csb_count_{r}_{c}"] = cell.get("count", 0)
        return True
    except Exception: return False

# 初期化
if "csb_rows" not in st.session_state:
    load_from_storage() or (st.session_state.update({"csb_rows": 5, "csb_cols": 5}))

# --- クエリパラメータによるJSリセット命令の処理 ---
if "reset_action" in st.query_params:
    action = st.query_params["reset_action"]
    if action == "count_only":
        # セッションとストレージの両方を確実に更新
        rows, cols = st.session_state.get("csb_rows", 5), st.session_state.get("csb_cols", 5)
        for r in range(rows):
            for c in range(cols):
                st.session_state[f"csb_count_{r}_{c}"] = 0
        validate_and_save() # 0の状態を保存
    elif action == "all":
        storage.delete_item(get_data_key())
        for k in list(st.session_state.keys()):
            if k.startswith("csb_"): del st.session_state[k]
        storage.set_item("csb_ver", "1")
    
    # パラメータを除去してリロード
    st.query_params.clear()
    st.rerun()

def on_change():
    validate_and_save()

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

# --- ビンゴ判定 ---
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
with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        current_state = {"rows": st.session_state.csb_rows, "cols": st.session_state.csb_cols, "cells": {f"{r}_{c}": {"label": st.session_state.get(f"csb_label_{r}_{c}"), "count": st.session_state.get(f"csb_count_{r}_{c}")} for r in range(st.session_state.csb_rows) for c in range(st.session_state.csb_cols)}}
        st.download_button(label="📥 保存", data=json.dumps(current_state, indent=2, ensure_ascii=False), file_name=f"bingo_{get_jst_now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)
    with c2:
        uploaded_file = st.file_uploader("📤 復元", type="json", label_visibility="collapsed")
        if uploaded_file and st.button("反映", use_container_width=True, type="primary"):
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
            except Exception: st.error("失敗")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    st.number_input("行数", 1, 15, key="csb_rows", on_change=on_change)
    st.number_input("列数", 1, 15, key="csb_cols", on_change=on_change)
    st.write("---")
    st.subheader("🚨 リセット")
    if st.button("🔢 カウントのみ0にする", use_container_width=True):
        st.components.v1.html("<script>if(window.confirm('カウントを0に戻しますか？')){const u=new URL(window.parent.location.href);u.searchParams.set('reset_action','count_only');window.parent.location.href=u.href;}</script>", height=0)
    if st.button("🚨 全てリセット", use_container_width=True, type="secondary"):
        st.components.v1.html("<script>if(window.confirm('全てのデータを消去しますか？')){const u=new URL(window.parent.location.href);u.searchParams.set('reset_action','all');window.parent.location.href=u.href;}</script>", height=0)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
