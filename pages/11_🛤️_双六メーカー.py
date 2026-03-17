import json

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.dice import roll_dice
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_grid_board,
    render_page_header,
    render_storage_controls,
    render_styled_number,
    wait_for_storage_load,
)
from src.utils.sugoroku import SugorokuBoard, calculate_new_position, create_board

st.set_page_config(page_title="双六メーカー", page_icon="🛤️", layout="wide")

# グローバルスタイルの適用
render_page_header()

st.title("🛤️ 双六メーカー")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())
DATA_KEY = "sugoroku_data_v3"

# セッション状態の初期化
if "sugoroku_board" not in st.session_state:
    saved_data = wait_for_storage_load(storage, DATA_KEY, "_sugoroku_initialized")
    if saved_data:
        try:
            if "board" in saved_data:
                st.session_state.sugoroku_board = SugorokuBoard(**saved_data["board"])
            else:
                st.session_state.sugoroku_board = create_board(10, False)
            st.session_state.current_pos = saved_data.get("current_pos", 0)
        except Exception:
            st.session_state.sugoroku_board = create_board(10, False)
            st.session_state.current_pos = 0
    else:
        st.session_state.sugoroku_board = create_board(10, False)
        st.session_state.current_pos = 0

    # 変更検知用のスナップショット
    snap_data = {
        "board": st.session_state.sugoroku_board.model_dump(),
        "current_pos": st.session_state.current_pos,
    }
    st.session_state.last_saved_sugoroku = json.dumps(snap_data, ensure_ascii=False)

    st.rerun()
    st.stop()

# 二重の安全策: 初期化が完了していない場合はここで停止
if "sugoroku_board" not in st.session_state:
    st.stop()

board: SugorokuBoard = st.session_state.sugoroku_board
current_state = {"board": board.model_dump(), "current_pos": st.session_state.current_pos}
is_dirty = st.session_state.last_saved_sugoroku != json.dumps(current_state, ensure_ascii=False)

# 盤面の設定（サイドバー）
with st.sidebar:
    st.header("⚙️ 設定")

    if is_dirty:
        st.warning("⚠️ 変更が保存されていません。")

    board_type_labels = ["スタートからゴール", "循環型（ループ）"]
    current_type_idx = 1 if board.is_loop else 0
    selected_type = st.radio("形式を選択", board_type_labels, index=current_type_idx)
    new_is_loop = selected_type == board_type_labels[1]

    new_num = st.slider("マスの数", 5, 50, board.total_tiles)

    if new_is_loop != board.is_loop or new_num != board.total_tiles:
        if st.button("⚠️ 設定を反映してリセット"):
            st.session_state.sugoroku_board = create_board(new_num, new_is_loop)
            st.session_state.current_pos = 0
            st.rerun()

    if st.button("🚨 盤面を完全に初期化", use_container_width=True):
        st.session_state.sugoroku_board = create_board(board.total_tiles, board.is_loop)
        st.session_state.current_pos = 0
        st.rerun()

# --- メインエリア：サイコロ操作 ---
st.subheader("🎲 サイコロを振って進む")
with st.container(border=True):
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        x_dice = st.number_input("個数", 1, 10, 1)
    with c2:
        n_dice = st.number_input("面の数", 1, 100, 6)
    with c3:
        st.write(" ")  # 余白
        if st.button("サイコロを振る！", use_container_width=True, type="primary"):
            results = roll_dice(x_dice, n_dice)
            dice_sum = sum(results)
            st.session_state.dice_last_result = dice_sum

            # 移動ロジック
            new_pos = calculate_new_position(st.session_state.current_pos, dice_sum, board.total_tiles, board.is_loop)

            if (
                not board.is_loop
                and new_pos == board.total_tiles - 1
                and st.session_state.current_pos != board.total_tiles - 1
            ):
                st.success("ゴール！おめでとう！")
                st.balloons()

            st.session_state.current_pos = new_pos

    if "dice_last_result" in st.session_state:
        render_styled_number("🎲 出目", st.session_state.dice_last_result)

st.write("")

# --- 盤面表示 ---
st.subheader("🛤️ 双六盤面")
cols_per_row = 5


def render_tile(idx):
    tile = board.tiles[idx]
    is_curr = st.session_state.current_pos == idx

    with st.container(border=True):
        if is_curr:
            st.markdown(
                """<div style='background-color:#FFEB3B; border-radius:8px; padding:4px; text-align:center; font-weight:bold; color:#000; margin-bottom:8px;'>📍 現在地</div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='text-align:center; opacity:0.6; margin-bottom:8px;'>No. {idx + 1}</div>",
                unsafe_allow_html=True,
            )

        # 名前編集
        new_val = st.text_input(f"t_{idx}", tile.text, key=f"in_{idx}", label_visibility="collapsed")
        if new_val != tile.text:
            tile.text = new_val

        # 手動移動ボタン
        if st.button("移動", key=f"b_{idx}", use_container_width=True):
            st.session_state.current_pos = idx
            st.rerun()

    # 矢印
    if idx < board.total_tiles - 1:
        arrow = "👇" if (idx + 1) % cols_per_row == 0 else "👉"
        st.markdown(
            f"<div style='text-align:center; font-size:24px; margin: 10px 0;'>{arrow}</div>", unsafe_allow_html=True
        )
    elif board.is_loop:
        st.markdown("<div style='text-align:center; margin-top:10px;'>⤴️ No.1へ</div>", unsafe_allow_html=True)


render_grid_board(board.total_tiles, cols_per_row, render_tile)


# データの管理
def on_load(data):
    if "board" in data:
        st.session_state.sugoroku_board = SugorokuBoard(**data["board"])
    if "current_pos" in data:
        st.session_state.current_pos = data["current_pos"]
    st.session_state.last_saved_sugoroku = json.dumps(data, ensure_ascii=False)


def on_save():
    st.session_state.last_saved_sugoroku = json.dumps(current_state, ensure_ascii=False)


render_storage_controls(
    storage=storage,
    storage_key=DATA_KEY,
    current_data=current_state,
    on_load_callback=on_load,
    on_save_callback=on_save,
    file_prefix="sugoroku",
)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
