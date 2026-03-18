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
DATA_KEY = "m3d_data_v3"  # キャッシュを完全にクリアするためにキーを更新

# --- 初期化とデータ復元 ---
if "m3d_state" not in st.session_state:
    saved_data = wait_for_storage_load(storage, DATA_KEY, "_m3d_initialized")
    if saved_data:
        st.session_state.m3d_state = migrate_minesweeper_3d_data(saved_data.get("state"))
    else:
        st.session_state.m3d_state = create_minesweeper_3d(5, 5, 5, 10)

    st.rerun()
    st.stop()

if "m3d_state" not in st.session_state or st.session_state.m3d_state is None:
    st.stop()

state: Minesweeper3DState = st.session_state.m3d_state

st.title("🧊 3Dマインスイーパー (β)")
st.warning("⚠️ **技術検証中**: この機能は現在、3D描画および通信の安定性を検証するためのプロトタイプです。")
st.caption("マウスで回転・スクロールでズーム。左クリックで開封、右クリック（またはCtrl+クリック）でフラグ。")

# --- ゲーム状態の表示 ---
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("地雷数", int(state.total_mines))
with col_info2:
    opened_count = sum(1 for c in state.cell_list if c.opened and not c.is_mine)
    safe_count = state.total_cells - state.total_mines
    st.metric("進行度", f"{int(opened_count)} / {int(safe_count)}")
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

# Base64 Data URI を生成 (TypeError 回避の最終手段)
# 文字列としての処理を Python 側で完結させ、iframe に直接流し込む
b64_uri = state.generate_base64_html(m3d_css, m3d_js)

# components.v1.iframe を使用し、src に Data URI を指定
# これにより Streamlit のシリアライズ制限を回避する
st.components.v1.iframe(src=b64_uri, height=600, scrolling=False)

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
        st.session_state.m3d_state = create_minesweeper_3d(int(nw), int(nh), int(nd), int(nm))
        st.rerun()

st.write("---")
st.info(
    "💡 **お知らせ**: このページは3次元空間でのマインスイーパーの挙動を検証するためのものであり、現時点ではゲームとしてのバランス調整や完全な機能実装は行われていません。あらかじめご了承ください。"
)


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
