import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.kurohige import KurohigeState, init_kurohige_state
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_grid_board,
    render_page_header,
    render_storage_controls,
    wait_for_storage_load,
)

st.set_page_config(page_title="黒ひげ危機一発", page_icon="☠️", layout="centered")

# グローバルスタイルの適用
render_page_header()

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "kh_state" not in st.session_state:
    saved_state = wait_for_storage_load(storage, "kurohige_state_v3", "_kh_initialized")
    if saved_state:
        try:
            st.session_state.kh_state = KurohigeState(**saved_state)
        except Exception:
            st.session_state.kh_state = init_kurohige_state()
    else:
        st.session_state.kh_state = init_kurohige_state()
    st.rerun()

state: KurohigeState = st.session_state.kh_state

st.markdown("<h1 style='text-align: center;'>☠️ 黒ひげ危機一発</h1>", unsafe_allow_html=True)

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    num_slots = st.slider("穴の数", 4, 24, state.num_slots)
    if st.button("ゲームをリセット", use_container_width=True, type="primary"):
        state.reset(num_slots)
        st.rerun()

# --- メインエリア ---
# JS/CSSの読み込み
try:
    with open("src/assets/kurohige/barrel.js", encoding="utf-8") as f:
        kh_js = f.read()
    with open("src/assets/kurohige/style.css", encoding="utf-8") as f:
        kh_css = f.read()
except Exception:
    kh_js = ""
    kh_css = ""

# JSアニメーション部分のレンダリング
html_template = f"""
<style>{kh_css}</style>
<div id="kurohige-app"></div>
<script>
    {kh_js}
    const config = {state.model_dump_json()};
    setupKurohige(config);
</script>
"""
st.components.v1.html(html_template, height=450)

st.write("")

# 状態表示
if state.status == "boom":
    st.error("🚀 ドカン！！！黒ひげが飛んでいきました！")
else:
    st.info(f"🗡️ 現在 {len(state.clicked_slots)} 本の剣が刺さっています。")

# 穴（ボタン）の表示
cols_per_row = 6


def render_slot(idx):
    slot_num = idx + 1
    is_clicked = idx in state.clicked_slots
    is_boom = state.status == "boom" and idx == state.target_slot

    label = f"{slot_num}\n🗡️" if is_clicked else (f"{slot_num}\n💥" if is_boom else f"{slot_num}")
    disabled = is_clicked or state.status == "boom"

    btn_type = "primary" if is_clicked else ("secondary" if not is_boom else "primary")

    if st.button(label, key=f"k_{idx}", disabled=disabled, use_container_width=True, type=btn_type):
        state.click_slot(idx)
        if state.status == "boom":
            st.snow()
        st.rerun()


render_grid_board(state.num_slots, cols_per_row, render_slot)


# データの管理
def on_load(data):
    st.session_state.kh_state = KurohigeState(**data)


render_storage_controls(
    storage=storage,
    storage_key="kurohige_state_v3",
    current_data=state,
    on_load_callback=on_load,
    file_prefix="kurohige",
    is_pydantic=True,
)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
