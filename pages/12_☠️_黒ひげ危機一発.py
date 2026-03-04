import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.kurohige import KurohigeState, init_kurohige_state
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header

st.set_page_config(page_title="黒ひげ危機一発", page_icon="☠️", layout="centered")

# グローバルスタイルの適用
render_page_header()

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "kh_state" not in st.session_state:
    saved_state = storage.get_item("kurohige_state_v2", is_json=True)
    if saved_state:
        st.session_state.kh_state = KurohigeState(**saved_state)
    else:
        st.session_state.kh_state = init_kurohige_state()

state: KurohigeState = st.session_state.kh_state

st.markdown("<h1 style='text-align: center;'>☠️ 黒ひげ危機一発</h1>", unsafe_allow_html=True)

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    num_slots = st.slider("穴の数", 4, 24, state.num_slots)
    if st.button("ゲームをリセット", use_container_width=True, type="primary"):
        state.reset(num_slots)
        storage.set_item("kurohige_state_v2", state.model_dump())
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

# JSコンポーネントのレンダリング
html_template = f"""
<style>{kh_css}</style>
<div id="kurohige-app"></div>
<script>
    {kh_js}
    const config = {state.model_dump_json()};
    setupKurohige(config);

    // JS側からのクリックイベントをリッスン
    window.addEventListener('slot_clicked', (e) => {{
        const index = e.detail.index;
        // Streamlit 側に値を渡すために hidden input と button を使うか、
        // URL query params を使う方法がある。
        // ここでは最も確実な URL query params 方式を採用。
        const url = new URL(window.location.href);
        url.searchParams.set('click_idx', index);
        window.parent.location.href = url.href;
    }});
</script>
"""

# Streamlit の Component 経由で JS を実行
# ※ st.components.v1.html は iframe なので、親ウィンドウへの通信が必要
# 今回はシンプルに、クリックされた index を st.query_params で受け取る
st.components.v1.html(html_template, height=550)

# クエリパラメータの監視
query_params = st.query_params
if "click_idx" in query_params:
    idx = int(query_params["click_idx"])
    # パラメータをクリア
    st.query_params.clear()

    if idx not in state.clicked_slots and state.status == "playing":
        state.click_slot(idx)
        storage.set_item("kurohige_state_v2", state.model_dump())
        if state.status == "boom":
            st.snow()
        st.rerun()

# 状態表示
if state.status == "boom":
    st.error("ドカン！！！黒ひげが飛んでいきました！")
elif state.status == "playing":
    st.info(f"現在 {len(state.clicked_slots)} 本の剣が刺さっています。")

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
