import json

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.count_support import (
    CounterItem,
    CountSupportSession,
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
CS_STORAGE_KEY = "cs_data_v3"

# セッション状態の初期化
if "cs_session" not in st.session_state:
    saved = storage.get_item(CS_STORAGE_KEY, is_json=True)
    if saved:
        st.session_state.cs_session = CountSupportSession(**saved)
    else:
        st.session_state.cs_session = CountSupportSession(
            items=[CounterItem(label="X"), CounterItem(label="Y"), CounterItem(label="Z")]
        )

session: CountSupportSession = st.session_state.cs_session


def save_to_storage():
    storage.set_item(CS_STORAGE_KEY, session.model_dump())


def weighted_counter_ui(idx: int):
    item = session.items[idx]
    with st.container(border=True):
        st.markdown(
            f"<div class='custom-counter-container'><h4>{item.label} カウンター</h4></div>", unsafe_allow_html=True
        )
        col_val, col_w = st.columns([2, 1])
        with col_val:
            new_count = st.number_input(
                f"{item.label}の数",
                value=item.count,
                key=f"val_{idx}",
                step=1,
            )
            if new_count != item.count:
                item.count = new_count
                save_to_storage()
        with col_w:
            new_weight = st.number_input(
                f"{item.label}の倍率",
                value=item.weight,
                key=f"weight_{idx}",
                step=0.1,
            )
            if new_weight != item.weight:
                item.weight = new_weight
                save_to_storage()

        current_weighted = calculate_weighted_value(item.count, item.weight)
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
    val_x = weighted_counter_ui(0)
    val_y = weighted_counter_ui(1)
    st.write("")
    render_result_box("X - Y の差分", f"{calculate_diff_xy(val_x, val_y):.1f}")

with col_main2:
    st.subheader("📊 追加集計")
    val_z = weighted_counter_ui(2)
    st.write("")
    render_result_box(
        "最終スコア (X-Y-Z)",
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
        st.download_button(
            "📥 保存",
            session.model_dump_json(indent=2),
            f"cs_{get_jst_now().strftime('%Y%m%d')}.json",
            "application/json",
            use_container_width=True,
        )
    with c2:
        uploaded_file = st.file_uploader("📤 復元", type="json", label_visibility="collapsed")
        if uploaded_file and st.button("反映", use_container_width=True, type="primary"):
            try:
                data_load = json.load(uploaded_file)
                st.session_state.cs_session = CountSupportSession(**data_load)
                save_to_storage()
                st.success("反映しました！")
                st.rerun()
            except Exception:
                st.error("読込失敗")

with st.sidebar:
    st.header("⚙️ 設定")
    st.write("---")
    st.subheader("🚨 リセット")
    if st.button("🚨 全てリセット", use_container_width=True, type="primary"):
        st.session_state.cs_session = CountSupportSession(
            items=[CounterItem(label="X"), CounterItem(label="Y"), CounterItem(label="Z")]
        )
        save_to_storage()
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
