import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.minesweeper import MinesweeperState, init_minesweeper_state
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header

st.set_page_config(page_title="マインスイーパー", page_icon="💣", layout="centered")

# グローバルスタイルの適用
render_page_header()

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "ms_state" not in st.session_state:
    saved_state = storage.get_item("ms_state_v2", is_json=True)
    if saved_state:
        st.session_state.ms_state = MinesweeperState(**saved_state)
    else:
        st.session_state.ms_state = init_minesweeper_state()

state: MinesweeperState = st.session_state.ms_state

st.markdown("<h1 style='text-align: center;'>💣 マインスイーパー</h1>", unsafe_allow_html=True)

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    ms_w = st.number_input("幅", 4, 20, state.width)
    ms_h = st.number_input("高さ", 4, 20, state.height)
    ms_mines = st.number_input("爆弾の数", 1, (ms_w * ms_h) - 1, state.num_mines)

    if st.button("ゲームをリセット", use_container_width=True, type="primary"):
        state.reset(ms_w, ms_h, ms_mines)
        storage.set_item("ms_state_v2", state.model_dump())
        st.rerun()

# --- メインエリア ---
# JS/CSSの読み込み
try:
    with open("src/assets/minesweeper/board.js", encoding="utf-8") as f:
        ms_js = f.read()
    with open("src/assets/minesweeper/style.css", encoding="utf-8") as f:
        ms_css = f.read()
except Exception:
    ms_js = ""
    ms_css = ""

# JSコンポーネントのレンダリング
html_template = f"""
<style>{ms_css}</style>
<div id="ms-app"></div>
<script>
    {ms_js}
    const config = {state.model_dump_json()};
    setupMinesweeper(config);

    // JS側からのアクションイベントをリッスン
    window.addEventListener('ms_action', (e) => {{
        const {{ r, c, action }} = e.detail;
        const url = new URL(window.location.href);
        url.searchParams.set('ms_r', r);
        url.searchParams.set('ms_c', c);
        url.searchParams.set('ms_action', action);
        window.parent.location.href = url.href;
    }});
</script>
"""

st.components.v1.html(html_template, height=min(600, state.height * 40 + 100))

# クエリパラメータの監視
query_params = st.query_params
if "ms_r" in query_params and "ms_c" in query_params:
    r = int(query_params["ms_r"])
    c = int(query_params["ms_c"])
    action = query_params["ms_action"]

    st.query_params.clear()

    if action == "reveal":
        state.reveal_tile(r, c)
    elif action == "flag":
        state.toggle_flag(r, c)

    storage.set_item("ms_state_v2", state.model_dump())
    if state.status == "won":
        st.balloons()
    st.rerun()

# 状態表示
if state.status == "won":
    st.success("🎉 クリア！おめでとうございます！")
elif state.status == "lost":
    st.error("💣 ドカン！ゲームオーバーです。")
else:
    st.info(f"🚩 爆弾の数: {state.num_mines}")

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
