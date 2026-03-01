import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.dice import roll_dice
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_grid_board,
    render_page_header,
    render_styled_number,
)
from src.utils.sugoroku import calculate_new_position, init_board_data

st.set_page_config(page_title="双六メーカー", page_icon="🛤️", layout="wide")

# グローバルスタイルの適用
render_page_header()

st.title("🛤️ 双六メーカー")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "just_reset_sugoroku" not in st.session_state:
    st.session_state.just_reset_sugoroku = False


def init_sugoroku_state():
    # 基本設定のロード
    if "sg_board_type" not in st.session_state:
        saved = storage.get_item("sg_board_type")
        st.session_state.sg_board_type = saved if saved else "スタートからゴール"

    if "sg_num_tiles" not in st.session_state:
        saved = storage.get_item("sg_num_tiles")
        st.session_state.sg_num_tiles = int(saved) if saved else 10

    if "current_pos" not in st.session_state:
        saved = storage.get_item("current_pos")
        st.session_state.current_pos = int(saved) if saved else 0

    if "board_data" not in st.session_state:
        st.session_state.board_data = {}


init_sugoroku_state()

# 盤面の設定（サイドバー）
with st.sidebar:
    st.header("⚙️ 設定")
    old_type = st.session_state.sg_board_type
    st.session_state.sg_board_type = st.radio(
        "形式を選択", ["スタートからゴール", "循環型（ループ）"], key="radio_type"
    )

    old_num = st.session_state.sg_num_tiles
    st.session_state.sg_num_tiles = st.slider("マスの数", 3, 50, st.session_state.sg_num_tiles, key="slider_num")

    if st.session_state.sg_board_type != old_type or st.session_state.sg_num_tiles != old_num:
        storage.set_item("sg_board_type", st.session_state.sg_board_type)
        storage.set_item("sg_num_tiles", st.session_state.sg_num_tiles)
        st.rerun()

    if st.button("盤面を完全に初期化", use_container_width=True):
        st.session_state.just_reset_sugoroku = True
        storage.clear_all_with_prefix("sg_", st.session_state)
        storage.clear_all_with_prefix("current_pos", st.session_state)
        st.session_state.current_pos = 0
        st.session_state.board_data = {}
        st.rerun()

if st.session_state.just_reset_sugoroku:
    st.session_state.just_reset_sugoroku = False

# 盤面データの生成とLocalStorageからの復元
total_tiles = st.session_state.sg_num_tiles
initial_data = init_board_data(total_tiles, st.session_state.sg_board_type)
for i in range(total_tiles):
    key = f"sg_tile_{i}"
    if key not in st.session_state.board_data:
        saved = storage.get_item(key)
        if saved:
            st.session_state.board_data[key] = saved
        else:
            st.session_state.board_data[key] = initial_data[key]

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
            is_loop = st.session_state.sg_board_type == "循環型（ループ）"
            new_pos = calculate_new_position(st.session_state.current_pos, dice_sum, total_tiles, is_loop)

            if not is_loop and new_pos == total_tiles - 1 and st.session_state.current_pos != total_tiles - 1:
                st.success("ゴール！おめでとう！")

            st.session_state.current_pos = new_pos
            storage.set_item("current_pos", new_pos)
            st.balloons()

    if "dice_last_result" in st.session_state:
        render_styled_number("🎲 出目", st.session_state.dice_last_result)

st.write("")

# --- 盤面表示 ---
st.subheader("🛤️ 双六盤面")
cols_per_row = 5


def render_tile(idx):
    key = f"sg_tile_{idx}"
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
        new_val = st.text_input(
            f"t_{idx}", st.session_state.board_data[key], key=f"in_{idx}", label_visibility="collapsed"
        )
        if new_val != st.session_state.board_data[key]:
            st.session_state.board_data[key] = new_val
            storage.set_item(key, new_val)

        # 手動移動ボタン
        if st.button("移動", key=f"b_{idx}", use_container_width=True):
            st.session_state.current_pos = idx
            storage.set_item("current_pos", idx)
            st.rerun()

    # 矢印
    if idx < total_tiles - 1:
        arrow = "👇" if (idx + 1) % cols_per_row == 0 else "👉"
        st.markdown(
            f"<div style='text-align:center; font-size:24px; margin: 10px 0;'>{arrow}</div>", unsafe_allow_html=True
        )
    elif st.session_state.sg_board_type == "循環型（ループ）":
        st.markdown("<div style='text-align:center; margin-top:10px;'>⤴️ No.1へ</div>", unsafe_allow_html=True)


render_grid_board(total_tiles, cols_per_row, render_tile)
render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
