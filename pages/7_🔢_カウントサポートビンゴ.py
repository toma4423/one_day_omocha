import json

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box
from src.utils.time import get_jst_now

# ページの設定
st.set_page_config(page_title="カウントサポートビンゴ", page_icon="🔢", layout="wide")

# スマホ対応用のカスタムCSS
st.markdown(
    """
    <style>
    .stButton > button { height: 60px !important; font-size: 20px !important; border-radius: 12px !important; }
    .stNumberInput input { font-size: 18px !important; text-align: center !important; }
    .stTextInput input { font-size: 16px !important; text-align: center !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🔢 カウントサポートビンゴ")

# --- ストレージ管理の定義 ---
storage = SafeStorage(LocalStorage())


def get_current_version():
    """URLまたはストレージから現在のデータバージョンを取得します。"""
    v_param = st.query_params.get("v", None)
    if v_param:
        return str(v_param)
    v_store = storage.get_item("csb_ver", is_json=False)
    return str(v_store) if v_store else "1"


def get_data_key(version=None):
    """指定した（または現在の）バージョンに基づいたデータキーを返します。"""
    v = version if version else get_current_version()
    return f"csb_data_v{v}"


def validate_and_save():
    """現在の状態を検証して JSON 保存します。"""
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
    """ストレージからデータを復元します。"""
    data = storage.get_item(get_data_key(), is_json=True)
    if not data:
        return False
    try:
        st.session_state.csb_rows, st.session_state.csb_cols = data.get("rows", 5), data.get("cols", 5)
        for pos, cell in data.get("cells", {}).items():
            r, c = pos.split("_")
            st.session_state[f"csb_label_{r}_{c}"], st.session_state[f"csb_count_{r}_{c}"] = (
                cell.get("label", ""),
                cell.get("count", 0),
            )
        return True
    except Exception:
        return False


# --- 初期化 ---
if "csb_ready" not in st.session_state:
    if not load_from_storage():
        st.session_state.csb_rows, st.session_state.csb_cols = 5, 5
    st.session_state.csb_ready = True


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
        label="JSONを保存",
        data=json_str,
        file_name=f"bingo_{get_jst_now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_file = st.file_uploader("JSONを読込", type="json")
    if uploaded_file and st.button("復元実行", use_container_width=True):
        try:
            d = json.load(uploaded_file)
            st.session_state.csb_rows, st.session_state.csb_cols = d["rows"], d["cols"]
            for k in list(st.session_state.keys()):
                if k.startswith("csb_label_") or k.startswith("csb_count_"):
                    del st.session_state[k]
            for pos, cell in d["cells"].items():
                r, c = pos.split("_")
                st.session_state[f"csb_label_{r}_{c}"], st.session_state[f"csb_count_{r}_{c}"] = (
                    cell["label"],
                    cell["count"],
                )
            validate_and_save()
            st.success("復元完了")
            st.rerun()
        except Exception:
            st.error("不正な形式です")

    st.write("---")
    if st.button("🚨 全てをリセット", use_container_width=True):
        # 1. 現在のバージョンのデータを物理削除
        storage.delete_item(get_data_key())

        # 2. バージョン番号を決定
        current_v = int(get_current_version())
        new_v = 1 if current_v >= 100 else current_v + 1

        # 3. 【重要】移行先のバージョン1（または次のバージョン）の古いデータが残っていればそれも掃除
        # これにより、100回後の周回遅れ不整合を完全に防ぐ
        storage.delete_item(get_data_key(version=new_v))

        # 4. バージョン更新
        st.query_params["v"] = str(new_v)
        storage.set_item("csb_ver", str(new_v))

        # 5. セッションクリア
        for k in list(st.session_state.keys()):
            if k.startswith("csb_"):
                del st.session_state[k]

        st.success(f"リセット完了 (次: Ver.{new_v})")
        st.rerun()

    st.info("自動保存：ブラウザ（LocalStorage）")

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
            st.text_input(f"L{r}{c}", key=lk, label_visibility="collapsed", on_change=on_change)
            c_m, c_v, c_p = st.columns([1, 1.5, 1])
            with c_m:
                st.button("－", key=f"m{r}{c}", use_container_width=True, on_click=on_step, args=(ck, -1))
            with c_v:
                st.number_input(f"N{r}{c}", key=ck, label_visibility="collapsed", step=1, on_change=on_change)
            with c_p:
                st.button("＋", key=f"p{r}{c}", use_container_width=True, on_click=on_step, args=(ck, 1))
render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
