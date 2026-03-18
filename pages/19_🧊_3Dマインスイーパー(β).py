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
DATA_KEY = "m3d_data_v4"  # 通信方式変更に合わせてキーを更新

# --- 初期化とデータ復元 ---
if "m3d_state" not in st.session_state:
    saved_data = wait_for_storage_load(storage, DATA_KEY, "_m3d_initialized")
    if saved_data:
        st.session_state.m3d_state = migrate_minesweeper_3d_data(saved_data.get("state"))
    else:
        st.session_state.m3d_state = create_minesweeper_3d(5, 5, 5, 10)

    # ウィジェットのキーを事前に初期化 (AttributeError防止)
    if "op_x" not in st.session_state:
        st.session_state.op_x = 0
    if "op_y" not in st.session_state:
        st.session_state.op_y = 0
    if "op_z" not in st.session_state:
        st.session_state.op_z = 0

    st.session_state.m3d_z_range = (0, 4)
    st.rerun()
    st.stop()

if "m3d_state" not in st.session_state or st.session_state.m3d_state is None:
    st.stop()

state: Minesweeper3DState = st.session_state.m3d_state

st.title("🧊 3Dマインスイーパー (β)")
st.warning(
    "⚠️ **技術検証中**: 3D画面からの直接操作（クリック）は現在調整中です。下の『操作パネル』からプレイしてください。"
)

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

# --- 視認性向上のためのフィルタリング設定 ---
with st.container(border=True):
    st.subheader("👁️ 視認性設定")
    z_min, z_max = st.slider("表示する深さ (Z軸範囲)", 0, state.depth - 1, (0, state.depth - 1), key="z_range_slider")

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

# Base64 Data URI を生成 (Z軸フィルタリング適用 + 選択座標ハイライト)
b64_uri = state.generate_base64_html(
    m3d_css,
    m3d_js,
    z_min=z_min,
    z_max=z_max,
    ix=st.session_state.op_x,
    iy=st.session_state.op_y,
    iz=st.session_state.op_z,
)
st.components.v1.iframe(src=b64_uri, height=600, scrolling=False)

# --- 操作パネル ---
with st.container(border=True):
    st.subheader("🕹️ 操作パネル")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
    with c1:
        ix = st.number_input("X座標", 0, state.width - 1, 0, key="op_x")
    with c2:
        iy = st.number_input("Y座標", 0, state.height - 1, 0, key="op_y")
    with c3:
        iz = st.number_input("Z座標", 0, state.depth - 1, 0, key="op_z")
    with c4:
        st.write("")
        cc1, cc2 = st.columns(2)
        if cc1.button("💎 開く", use_container_width=True, type="primary", disabled=state.game_over or state.won):
            st.session_state.m3d_state = open_cell_3d(state, ix, iy, iz)
            st.rerun()
        if cc2.button("🚩 フラグ", use_container_width=True, disabled=state.game_over or state.won):
            st.session_state.m3d_state = toggle_flag_3d(state, ix, iy, iz)
            st.rerun()

st.write("---")

# --- 設定と管理 ---
with st.expander("⚙️ ゲーム設定"):
    st.subheader("🆕 新規ゲーム開始")
    nc1, nc2, nc3, nc4 = st.columns(4)
    with nc1:
        nw = st.slider("幅(X)", 3, 10, 5)
    with nc2:
        nh = st.slider("高さ(Y)", 3, 10, 5)
    with nc3:
        nd = st.slider("奥行(Z)", 3, 10, 5)
    with nc4:
        nm = st.number_input("地雷数", 1, 100, 10)

    if st.button("設定を適用してリセット", use_container_width=True):
        st.session_state.m3d_state = create_minesweeper_3d(int(nw), int(nh), int(nd), int(nm))
        st.rerun()

st.info(
    "💡 **遊び方**: 3D空間をマウスでドラッグして回転させ、中を覗き込んで地雷を探します。上のスライダーで特定の層だけを表示すると見つけやすくなります。"
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
