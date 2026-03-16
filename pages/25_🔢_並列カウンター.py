import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.parallel_counter import (
    ParallelCounterItem,
    add_counter,
    migrate_parallel_counter_data,
    remove_counter,
    update_counter_name,
    update_counter_value,
)
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_storage_controls,
    wait_for_storage_load,
)

st.set_page_config(page_title="並列カウンター", page_icon="🔢", layout="wide")

# グローバルスタイルの適用
render_page_header()

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "parallel_counters" not in st.session_state:
    saved_data = wait_for_storage_load(storage, "parallel_counters_v2", "_pc_initialized")
    try:
        st.session_state.parallel_counters = migrate_parallel_counter_data(saved_data)
    except Exception:
        st.session_state.parallel_counters = []
    st.rerun()
    st.stop()

# 二重の安全策: 初期化が完了していない場合はここで停止
if "parallel_counters" not in st.session_state:
    st.stop()

if "last_updated_id" not in st.session_state:
    st.session_state.last_updated_id = None

# カスタムスタイルの適用
st.markdown(
    """
    <style>
    .st-emotion-cache-16idsys, .st-emotion-cache-1r6slb0 { border-radius: 16px !important; }
    .pulse-effect { animation: pulse-animation 0.4s ease-out; }
    @keyframes pulse-animation {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); color: #007bff; }
        100% { transform: scale(1); }
    }
    .plus-btn button { background-color: #007bff !important; color: white !important; }
    .minus-btn button { background-color: #f8f9fa !important; color: #333 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; font-weight: 900; color: #333;'>🔢 並列カウンター</h1>", unsafe_allow_html=True
)

# ツールバー
col_actions, col_empty = st.columns([1, 4])
with col_actions:
    if st.button("➕ カウントを追加", use_container_width=True, type="primary"):
        st.session_state.parallel_counters = add_counter(st.session_state.parallel_counters)
        st.rerun()

st.write("")

# カウンターの表示
if not st.session_state.parallel_counters:
    st.info("カウンターがありません。")
else:
    cols = st.columns(3)
    for i, counter in enumerate(st.session_state.parallel_counters):
        counter: ParallelCounterItem
        with cols[i % 3]:
            with st.container(border=True):
                new_name = st.text_input(
                    "名前", value=counter.name, key=f"name_{counter.id}", label_visibility="collapsed"
                )
                if new_name != counter.name:
                    st.session_state.parallel_counters = update_counter_name(
                        st.session_state.parallel_counters, counter.id, new_name
                    )

                pulse_class = "pulse-effect" if st.session_state.last_updated_id == counter.id else ""
                st.markdown(f"<div class='large-value {pulse_class}'>{counter.value}</div>", unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                with b1:
                    st.markdown("<div class='minus-btn'>", unsafe_allow_html=True)
                    if st.button("− 減らす", key=f"minus_{counter.id}", use_container_width=True):
                        st.session_state.parallel_counters = update_counter_value(
                            st.session_state.parallel_counters, counter.id, -1
                        )
                        st.session_state.last_updated_id = counter.id
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with b2:
                    st.markdown("<div class='plus-btn'>", unsafe_allow_html=True)
                    if st.button("＋ 増やす", key=f"plus_{counter.id}", use_container_width=True):
                        st.session_state.parallel_counters = update_counter_value(
                            st.session_state.parallel_counters, counter.id, 1
                        )
                        st.session_state.last_updated_id = counter.id
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                r1, r2 = st.columns(2)
                with r1:
                    if st.button("🔄", key=f"reset_{counter.id}", use_container_width=True, help="リセット"):
                        for item in st.session_state.parallel_counters:
                            if item.id == counter.id:
                                item.value = 0
                                break
                        st.rerun()
                with r2:
                    if st.button("🗑️", key=f"del_{counter.id}", use_container_width=True, help="削除"):
                        st.session_state.parallel_counters = remove_counter(
                            st.session_state.parallel_counters, counter.id
                        )
                        st.rerun()


# データの管理
def on_load(data):
    st.session_state.parallel_counters = migrate_parallel_counter_data(data)


current_data = [c.model_dump() for c in st.session_state.parallel_counters]

render_storage_controls(
    storage=storage,
    storage_key="parallel_counters_v2",
    current_data=current_data,
    on_load_callback=on_load,
    file_prefix="parallel_counters",
)

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 一括操作")
    if st.button("🔄 すべてリセット", use_container_width=True):
        for item in st.session_state.parallel_counters:
            item.value = 0
        st.rerun()
    if st.button("🗑️ すべて削除", use_container_width=True):
        if st.checkbox("削除を確定"):
            st.session_state.parallel_counters = []
            st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
