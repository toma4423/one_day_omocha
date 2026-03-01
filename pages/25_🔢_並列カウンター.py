import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.parallel_counter import (
    add_counter,
    migrate_parallel_counter_data,
    remove_counter,
    update_counter_name,
    update_counter_value,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box

st.set_page_config(page_title="並列カウンター", page_icon="🔢", layout="wide")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "parallel_counters" not in st.session_state:
    saved_data = storage.get_item("parallel_counters", is_json=True)
    st.session_state.parallel_counters = migrate_parallel_counter_data(saved_data)

st.markdown("<h1 style='text-align: center;'>🔢 並列カウンター</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: gray;'>複数の項目を同時にカウントできます。ブラウザに自動保存されます。</p>",
    unsafe_allow_html=True,
)

# ツールバー（上部）
col_actions, col_empty = st.columns([1, 4])
with col_actions:
    if st.button("➕ カウンターを追加", use_container_width=True, type="primary"):
        st.session_state.parallel_counters = add_counter(st.session_state.parallel_counters)
        storage.set_item("parallel_counters", st.session_state.parallel_counters)
        st.rerun()

st.write("---")

# カウンターのグリッド表示 (3列)
if not st.session_state.parallel_counters:
    st.info("カウンターがありません。「追加」ボタンから作成してください。")
else:
    # 3列のレイアウト
    cols = st.columns(3)

    for i, counter in enumerate(st.session_state.parallel_counters):
        col_idx = i % 3
        with cols[col_idx]:
            # カウンターのカード風表示
            with st.container(border=True):
                # 名前入力
                new_name = st.text_input(
                    "名前", value=counter["name"], key=f"name_input_{counter['id']}", label_visibility="collapsed"
                )
                if new_name != counter["name"]:
                    st.session_state.parallel_counters = update_counter_name(
                        st.session_state.parallel_counters, counter["id"], new_name
                    )
                    storage.set_item("parallel_counters", st.session_state.parallel_counters)

                # 数値表示
                st.markdown(
                    f"<div style='text-align: center; font-size: 48px; font-weight: bold; padding: 10px 0;'>{counter['value']}</div>",
                    unsafe_allow_html=True,
                )

                # 操作ボタン
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("➖ 減らす", key=f"minus_{counter['id']}", use_container_width=True):
                        st.session_state.parallel_counters = update_counter_value(
                            st.session_state.parallel_counters, counter["id"], -1
                        )
                        storage.set_item("parallel_counters", st.session_state.parallel_counters)
                        st.rerun()
                with b2:
                    if st.button("➕ 増やす", key=f"plus_{counter['id']}", use_container_width=True):
                        st.session_state.parallel_counters = update_counter_value(
                            st.session_state.parallel_counters, counter["id"], 1
                        )
                        storage.set_item("parallel_counters", st.session_state.parallel_counters)
                        st.rerun()

                # 削除とリセット
                st.write("")
                r1, r2 = st.columns(2)
                with r1:
                    if st.button("🔄 リセット", key=f"reset_{counter['id']}", use_container_width=True):
                        # 0にリセット
                        for item in st.session_state.parallel_counters:
                            if item["id"] == counter["id"]:
                                item["value"] = 0
                                break
                        storage.set_item("parallel_counters", st.session_state.parallel_counters)
                        st.rerun()
                with r2:
                    if st.button("🗑️ 削除", key=f"del_{counter['id']}", use_container_width=True):
                        st.session_state.parallel_counters = remove_counter(
                            st.session_state.parallel_counters, counter["id"]
                        )
                        storage.set_item("parallel_counters", st.session_state.parallel_counters)
                        st.rerun()

st.write("---")

# サイドバー設定
with st.sidebar:
    st.subheader("⚙️ 一括操作")
    if st.button("🔄 すべての値をリセット", use_container_width=True):
        for item in st.session_state.parallel_counters:
            item["value"] = 0
        storage.set_item("parallel_counters", st.session_state.parallel_counters)
        st.success("すべてリセットしました")
        st.rerun()

    if st.button("🗑️ すべてのカウンターを削除", use_container_width=True):
        st.session_state.parallel_counters = []
        storage.set_item("parallel_counters", [])
        st.success("すべて削除しました")
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
