import streamlit as st
import random
from streamlit_local_storage import LocalStorage
from src.utils.storage import SafeStorage
from src.utils.time import get_jst_now

st.set_page_config(page_title="黒ひげ危機一発", page_icon="☠️")

# スマホ対応CSS
st.markdown("""
    <style>
    .stButton > button {
        height: 80px !important;
        font-size: 20px !important;
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("☠️ 黒ひげ危機一発")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if 'kurohige_status' not in st.session_state:
    saved_status = storage.get_item('kh_status')
    st.session_state.kurohige_status = saved_status if saved_status else "ready"

if 'kurohige_target' not in st.session_state:
    saved_target = storage.get_item('kh_target')
    st.session_state.kurohige_target = int(saved_target) if saved_target is not None else -1

if 'kurohige_clicked' not in st.session_state:
    saved_clicked = storage.get_item('kh_clicked')
    st.session_state.kurohige_clicked = saved_clicked if saved_clicked is not None else []

def reset_game(num_slots):
    st.session_state.kurohige_target = random.randint(0, num_slots - 1)
    st.session_state.kurohige_clicked = []
    st.session_state.kurohige_status = "playing"
    # ストレージも更新
    storage.set_item('kh_target', st.session_state.kurohige_target)
    storage.set_item('kh_clicked', [])
    storage.set_item('kh_status', "playing")

num_slots = st.sidebar.slider("穴の数", 4, 24, 12)

# ゲーム開始またはリセット
if st.session_state.kurohige_status == "ready" or st.sidebar.button("リセット"):
    reset_game(num_slots)
    st.rerun()

# 状態に応じたヘッダー表示
if st.session_state.kurohige_status == "boom":
    st.markdown("<h1 style='text-align:center; font-size:100px;'>🚀 🏴‍☠️</h1><h2 style='text-align:center; color:red;'>ドカン！！！</h2>", unsafe_allow_html=True)
    st.snow()
else:
    st.markdown("<h1 style='text-align:center; font-size:100px;'>🛢️</h1>", unsafe_allow_html=True)

# 穴（ボタン）の表示
cols_per_row = 4
for i in range(0, num_slots, cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx < num_slots:
            with col:
                # スロット番号を表示するためのラベル
                slot_num = idx + 1
                
                # すでにクリックされたか、爆発済みの場合は無効化
                if idx in st.session_state.kurohige_clicked:
                    # セーフの表示を 🗡️ セーフ に変更
                    st.button(f"{slot_num}\n🗡️ セーフ", key=f"k_{idx}", disabled=True, use_container_width=True)
                elif st.session_state.kurohige_status == "boom":
                    st.button(f"{slot_num}\n🕳️", key=f"k_{idx}", disabled=True, use_container_width=True)
                else:
                    # 番号付きのボタン
                    if st.button(f"{slot_num}\n❓", key=f"k_{idx}", use_container_width=True):
                        if idx == st.session_state.kurohige_target:
                            st.session_state.kurohige_status = "boom"
                            storage.set_item('kh_status', "boom")
                        else:
                            st.session_state.kurohige_clicked.append(idx)
                            storage.set_item('kh_clicked', st.session_state.kurohige_clicked)
                        st.rerun()

st.sidebar.write("---")
st.sidebar.info("自動保存：ブラウザ（LocalStorage）")
