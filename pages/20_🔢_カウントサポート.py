import json

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.count_support import (
    calculate_diff_xy,
    calculate_final_score,
    calculate_weighted_value,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header, render_result_box
from src.utils.time import get_jst_now

st.set_page_config(page_title="カウントサポート", page_icon="🔢", layout="wide")

# グローバルスタイルの適用
render_page_header()

# 外部CSSの読み込み
try:
    with open("src/assets/counter/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())
CS_STORAGE_KEY = "cs_data_v2" # キーを刷新して安定化

# セッション状態の初期化
if "cs_reset_id" not in st.session_state:
    st.session_state.cs_reset_id = 0

def save_to_storage():
    data = {
        "x": st.session_state.get("cs_x", 0),
        "y": st.session_state.get("cs_y", 0),
        "z": st.session_state.get("cs_z", 0),
        "weight_x": st.session_state.get("cs_weight_x", 1.0),
        "weight_y": st.session_state.get("cs_weight_y", 1.0),
        "weight_z": st.session_state.get("cs_weight_z", 1.0),
    }
    storage.set_item(CS_STORAGE_KEY, data)

def load_from_storage():
    data = storage.get_item(CS_STORAGE_KEY, is_json=True)
    if data:
        st.session_state.cs_x = data.get("x", 0)
        st.session_state.cs_y = data.get("y", 0)
        st.session_state.cs_z = data.get("z", 0)
        st.session_state.cs_weight_x = data.get("weight_x", 1.0)
        st.session_state.cs_weight_y = data.get("weight_y", 1.0)
        st.session_state.cs_weight_z = data.get("weight_z", 1.0)
        return True
    return False

# 初期化ロジック
if "cs_x" not in st.session_state:
    if not load_from_storage():
        st.session_state.cs_x = 0
        st.session_state.cs_y = 0
        st.session_state.cs_z = 0
        st.session_state.cs_weight_x = 1.0
        st.session_state.cs_weight_y = 1.0
        st.session_state.cs_weight_z = 1.0

def weighted_counter_ui(label: str, key_val: str, key_weight: str):
    rid = st.session_state.cs_reset_id
    with st.container(border=True):
        st.markdown(f"<div class='custom-counter-container'><h4>{label} カウンター</h4></div>", unsafe_allow_html=True)
        col_val, col_w = st.columns([2, 1])
        with col_val:
            st.session_state[key_val] = st.number_input(
                f"{label}の数",
                value=int(st.session_state.get(key_val, 0)),
                key=f"{key_val}_{rid}",
                on_change=save_to_storage,
                step=1
            )
        with col_w:
            st.session_state[key_weight] = st.number_input(
                f"{label}の倍率",
                value=float(st.session_state.get(key_weight, 1.0)),
                key=f"{key_weight}_{rid}",
                step=0.1,
                on_change=save_to_storage,
            )
        current_weighted = calculate_weighted_value(st.session_state[key_val], st.session_state[key_weight])
        st.markdown(
            f"<p style='text-align:right; color:#007bff; font-weight:bold; font-size:16px;'>算出値: {current_weighted:.1f}</p>",
            unsafe_allow_html=True,
        )
    return current_weighted

st.title("🔢 カウントサポート")
st.markdown("数値や倍率を変更すると、自動的に計算と保存が行われます。")

col_main1, col_main2 = st.columns(2)
with col_main1:
    st.subheader("📊 基本集計")
    val_x = weighted_counter_ui("X", "cs_x", "cs_weight_x")
    val_y = weighted_counter_ui("Y", "cs_y", "cs_weight_y")
    st.write("")
    render_result_box("X - Y の差分", f"{calculate_diff_xy(val_x, val_y):.1f}")

with col_main2:
    st.subheader("📊 追加集計")
    val_z = weighted_counter_ui("Z", "cs_z", "cs_weight_z")
    st.write("")
    render_result_box(
        "最終スコア (X-Y+Z)",
        f"{calculate_final_score(val_x, val_y, val_z):.1f}",
        bg_color="#E8F5E9",
        border_color="#2E7D32",
        text_color="#2E7D32",
        font_size=64,
    )

st.write("---")
with st.container(border=True):
    st.subheader("📁 データの保存と読み込み")
    c1, c2 = st.columns(2)
    with c1:
        current_data = {"x": st.session_state.cs_x, "y": st.session_state.cs_y, "z": st.session_state.cs_z, "weight_x": st.session_state.cs_weight_x, "weight_y": st.session_state.cs_weight_y, "weight_z": st.session_state.cs_weight_z}
        st.download_button("📥 保存", json.dumps(current_data, indent=2), f"cs_{get_jst_now().strftime('%Y%m%d')}.json", "application/json", use_container_width=True)
    with c2:
        uploaded_file = st.file_uploader("📤 復元", type="json", label_visibility="collapsed")
        if uploaded_file and st.button("反映", use_container_width=True, type="primary", key="btn_apply_cs"):
            try:
                data_load = json.load(uploaded_file)
                st.session_state.cs_x = data_load.get("x", 0)
                st.session_state.cs_y = data_load.get("y", 0)
                st.session_state.cs_z = data_load.get("z", 0)
                st.session_state.cs_weight_x = data_load.get("weight_x", 1.0)
                st.session_state.cs_weight_y = data_load.get("weight_y", 1.0)
                st.session_state.cs_weight_z = data_load.get("weight_z", 1.0)
                st.session_state.cs_reset_id += 1
                save_to_storage()
                st.success("反映しました！")
                st.rerun()
            except Exception: st.error("読込失敗")

with st.sidebar:
    st.header("⚙️ 設定")
    st.write("---")
    st.subheader("🚨 リセット")
    with st.popover("🚨 全てリセット", use_container_width=True):
        st.error("全ての数値をリセットして初期状態に戻します。")
        if st.button("実行する", key="confirm_cs_reset", type="primary", use_container_width=True):
            storage.delete_item(CS_STORAGE_KEY)
            # 管理キー以外を削除
            keep_keys = {"cs_reset_id"}
            for k in list(st.session_state.keys()):
                if k.startswith("cs_") and k not in keep_keys:
                    del st.session_state[k]
            st.session_state.cs_reset_id += 1
            st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
