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
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_result_box,
    render_storage_controls,
    wait_for_storage_load,
)

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
CS_STORAGE_KEY = "cs_data_v4"

# セッション状態の初期化
if "_cs_initialized" not in st.session_state:
    saved = wait_for_storage_load(storage, CS_STORAGE_KEY, "_cs_initialized")
    if saved:
        st.session_state.cs_session = CountSupportSession(**saved)
    else:
        st.session_state.cs_session = CountSupportSession(
            items=[CounterItem(label="X"), CounterItem(label="Y"), CounterItem(label="Z")]
        )
    st.rerun()

session: CountSupportSession = st.session_state.cs_session


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
        with col_w:
            new_weight = st.number_input(
                f"{item.label}の倍率",
                value=item.weight,
                key=f"weight_{idx}",
                step=0.1,
            )
            if new_weight != item.weight:
                item.weight = new_weight

        current_weighted = calculate_weighted_value(item.count, item.weight)
        st.markdown(
            f"<p style='text-align:right; color:#007bff; font-weight:bold; font-size:16px;'>算出値: {current_weighted:.1f}</p>",
            unsafe_allow_html=True,
        )
    return current_weighted


st.title("🔢 カウントサポート")
st.markdown("数値や倍率を変更したら、ページ下部で保存してください。")

# モバイルでは縦に並べる
col_main1, col_main2 = st.columns([1, 1])
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


# データの管理
def on_load(data):
    st.session_state.cs_session = CountSupportSession(**data)


render_storage_controls(
    storage=storage,
    storage_key=CS_STORAGE_KEY,
    current_data=session,
    on_load_callback=on_load,
    file_prefix="count_support",
    is_pydantic=True,
)

with st.sidebar:
    st.header("⚙️ 設定")
    st.write("---")
    st.subheader("🚨 リセット")
    if st.button("🚨 全てリセット", use_container_width=True, type="primary"):
        st.session_state.cs_session = CountSupportSession(
            items=[CounterItem(label="X"), CounterItem(label="Y"), CounterItem(label="Z")]
        )
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
