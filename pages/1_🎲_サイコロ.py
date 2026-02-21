import streamlit as st
import pandas as pd
from datetime import datetime
from src.utils.dice import roll_dice
from src.utils.styles import render_result_box
from streamlit_local_storage import LocalStorage
from src.utils.storage import SafeStorage

st.set_page_config(page_title="サイコロ", page_icon="🎲", layout="wide")

# スマホ対応CSS
st.markdown("""
    <style>
    .stButton > button {
        height: 60px !important;
        font-size: 20px !important;
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎲 サイコロ")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# 履歴の初期化（LocalStorage から復元）
if 'dice_history' not in st.session_state:
    saved_history = storage.get_item('dice_history')
    st.session_state.dice_history = saved_history if saved_history is not None else []

# サイドバー操作
with st.sidebar:
    st.header("⚙️ 設定")
    if st.button("履歴をリセット", use_container_width=True):
        st.session_state.dice_history = []
        storage.set_item('dice_history', [])
        st.success("履歴を消去しました")
        st.rerun()

col1, col2 = st.columns(2)
with col1: x = st.number_input("ダイスの数 (x)", 1, 100, 1)
with col2: n = st.number_input("ダイスの目の数 (n)", 1, 1000, 6)

if st.button("サイコロを振る！", use_container_width=True):
    results = roll_dice(x, n)
    total = sum(results)
    
    # 履歴に追加
    new_record = {
        "時刻": datetime.now().strftime("%H:%M:%S"),
        "設定": f"{x}d{n}",
        "出目合計": total
    }
    st.session_state.dice_history.insert(0, new_record)
    storage.set_item('dice_history', st.session_state.dice_history)
    
    st.write("---")
    render_result_box("結果", total)
    st.balloons()

# 履歴表示エリア
st.write("---")
st.subheader("📜 サイコロの履歴")
if st.session_state.dice_history:
    history_df = pd.DataFrame(st.session_state.dice_history)
    st.table(history_df)
else:
    st.write("履歴はありません。")
