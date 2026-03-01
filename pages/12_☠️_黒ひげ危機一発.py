import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.kurohige import check_slot, init_kurohige
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_grid_board,
    render_page_header,
)

st.set_page_config(page_title="黒ひげ危機一発", page_icon="☠️", layout="centered")

# グローバルスタイルの適用
render_page_header()

st.markdown("<h1 style='text-align: center;'>☠️ 黒ひげ危機一発</h1>", unsafe_allow_html=True)

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "kurohige_status" not in st.session_state:
    saved_status = storage.get_item("kh_status")
    st.session_state.kurohige_status = saved_status if saved_status else "ready"

if "kurohige_target" not in st.session_state:
    saved_target = storage.get_item("kh_target")
    st.session_state.kurohige_target = int(saved_target) if saved_target is not None else -1

if "kurohige_clicked" not in st.session_state:
    saved_clicked = storage.get_item("kh_clicked")
    st.session_state.kurohige_clicked = saved_clicked if saved_clicked else []


def reset_game(num_slots):
    st.session_state.kurohige_target = init_kurohige(num_slots)
    st.session_state.kurohige_clicked = []
    st.session_state.kurohige_status = "playing"
    # ストレージも更新
    storage.set_item("kh_target", st.session_state.kurohige_target)
    storage.set_item("kh_clicked", [])
    storage.set_item("kh_status", "playing")


num_slots = st.sidebar.slider("穴の数", 4, 24, 12)

# ゲーム開始またはリセット
if st.session_state.kurohige_status == "ready" or st.sidebar.button("リセット"):
    reset_game(num_slots)
    st.rerun()

# 状態に応じたヘッダー表示
with st.container(border=True):
    if st.session_state.kurohige_status == "boom":
        st.markdown(
            "<h1 style='text-align:center; font-size:100px; margin:0;'>🚀 🏴‍☠️</h1><h2 style='text-align:center; color:#ff4b4b; font-weight:900;'>ドカン！！！</h2>",
            unsafe_allow_html=True,
        )
        st.snow()
    else:
        st.markdown("<h1 style='text-align:center; font-size:100px; margin:0;'>🛢️</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align:center; color:gray;'>剣を刺して黒ひげを飛ばさないように気をつけて！</p>",
            unsafe_allow_html=True,
        )

st.write("")

# 穴（ボタン）の表示
cols_per_row = 4


def render_slot(idx):
    slot_num = idx + 1
    # すでにクリックされたか、爆発済みの場合は無効化
    if idx in st.session_state.kurohige_clicked:
        st.button(f"{slot_num}\n🗡️ ｾｰﾌ", key=f"k_{idx}", disabled=True, use_container_width=True)
    elif st.session_state.kurohige_status == "boom":
        st.button(f"{slot_num}\n🕳️", key=f"k_{idx}", disabled=True, use_container_width=True)
    else:
        # 番号付きのボタン
        if st.button(f"{slot_num}\n❓", key=f"k_{idx}", use_container_width=True, type="secondary"):
            if check_slot(idx, st.session_state.kurohige_target) == "boom":
                st.session_state.kurohige_status = "boom"
                storage.set_item("kh_status", "boom")
            else:
                st.session_state.kurohige_clicked.append(idx)
                storage.set_item("kh_clicked", st.session_state.kurohige_clicked)
            st.rerun()


render_grid_board(num_slots, cols_per_row, render_slot)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
