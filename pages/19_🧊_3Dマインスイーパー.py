import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.minesweeper_3d import (
    Minesweeper3DState,
    create_minesweeper_3d,
    migrate_minesweeper_3d_data,
    open_cell_3d,
    toggle_flag_3d,
)
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_storage_controls,
    wait_for_storage_load,
)

# ページ基本設定
st.set_page_config(page_title="3Dマインスイーパー", page_icon="🧊", layout="wide")

# グローバルスタイルの適用
render_page_header()

storage = SafeStorage(LocalStorage())
DATA_KEY = "m3d_data_v1"

# --- 初期化とデータ復元 ---
if "m3d_state" not in st.session_state:
    saved_data = wait_for_storage_load(storage, DATA_KEY, "_m3d_initialized")
    if saved_data:
        st.session_state.m3d_state = migrate_minesweeper_3d_data(saved_data.get("state"))
    else:
        st.session_state.m3d_state = create_minesweeper_3d(5, 5, 5, 10)

    st.rerun()
    st.stop()

# 二重の安全策
if "m3d_state" not in st.session_state or st.session_state.m3d_state is None:
    st.stop()

state: Minesweeper3DState = st.session_state.m3d_state

st.title("🧊 3Dマインスイーパー")
st.caption("マウスで回転・スクロールでズーム。左クリックで開封、右クリック（またはCtrl+クリック）でフラグ。")

# --- ゲーム状態の表示 ---
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("地雷数", state.total_mines)
with col_info2:
    opened_count = sum(1 for c in state.cells.values() if c.opened and not c.is_mine)
    safe_count = state.total_cells - state.total_mines
    st.metric("進行度", f"{opened_count} / {safe_count}")
with col_info3:
    if state.game_over:
        st.error("💥 GAME OVER!")
    elif state.won:
        st.success("🎉 YOU WIN!")
    else:
        st.info("🎮 プレイ中...")

# --- 3D描画コンポーネント ---
m3d_css = ""
m3d_js = ""
try:
    with open("src/assets/minesweeper_3d/style.css", encoding="utf-8") as f:
        m3d_css = f.read()
    with open("src/assets/minesweeper_3d/game.js", encoding="utf-8") as f:
        m3d_js = f.read()
except Exception as e:
    st.error(f"アセットの読み込みに失敗しました: {e}")

# コアロジック側で安全にHTMLを生成
full_html = state.generate_safe_html(m3d_css, m3d_js)

# key は固定文字列を使用して安定させる
st.components.v1.html(full_html, height=600, key="m3d_canvas_final")

# --- 補助UI: 直接座標指定で開く ---
with st.expander("🛠️ 手動操作・設定"):
    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
    with c1:
        ix = st.number_input("X", 0, state.width - 1, 0)
    with c2:
        iy = st.number_input("Y", 0, state.height - 1, 0)
    with c3:
        iz = st.number_input("Z", 0, state.depth - 1, 0)
    with c4:
        st.write("")
        cc1, cc2 = st.columns(2)
        if cc1.button("開く", use_container_width=True):
            st.session_state.m3d_state = open_cell_3d(state, ix, iy, iz)
            st.rerun()
        if cc2.button("フラグ", use_container_width=True):
            st.session_state.m3d_state = toggle_flag_3d(state, ix, iy, iz)
            st.rerun()

    st.write("---")
    st.subheader("🆕 新規ゲーム")
    nc1, nc2, nc3, nc4 = st.columns(4)
    with nc1:
        nw = st.slider("幅", 3, 10, 5)
    with nc2:
        nh = st.slider("高さ", 3, 10, 5)
    with nc3:
        nd = st.slider("奥行", 3, 10, 5)
    with nc4:
        nm = st.number_input("地雷数", 1, 100, 10)

    if st.button("ゲームをリセットして開始", use_container_width=True, type="primary"):
        st.session_state.m3d_state = create_minesweeper_3d(nw, nh, nd, nm)
        st.rerun()


# --- データの保存 ---
def on_save():
    pass


render_storage_controls(
    storage=storage,
    storage_key=DATA_KEY,
    current_data={"state": state.model_dump()},
    on_load_callback=lambda d: st.session_state.update({"m3d_state": migrate_minesweeper_3d_data(d.get("state"))}),
    on_save_callback=on_save,
    file_prefix="m3d_data",
)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
