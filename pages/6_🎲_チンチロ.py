import pandas as pd
import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.dice import DICE_EMOJI, HAND_RANK, evaluate_hand, roll_dice
from src.utils.storage import SafeStorage
from src.utils.styles import display_dice_html, render_dice_animation, render_donation_box
from src.utils.time import get_jst_now

st.set_page_config(page_title="チンチロ", page_icon="🎲", layout="wide")

# スマホ対応CSS
st.markdown(
    """
    <style>
    .stButton > button {
        height: 60px !important;
        font-size: 20px !important;
        border-radius: 12px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎲 チンチロリン")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# --- セッション状態の初期化 ---
if "cc_dice" not in st.session_state:
    st.session_state.cc_dice = [1, 2, 3]
if "cc_hand" not in st.session_state:
    st.session_state.cc_hand = None

# 履歴の初期化（LocalStorage から復元）
if "cc_history" not in st.session_state:
    saved_history = storage.get_item("cc_history")
    st.session_state.cc_history = saved_history if saved_history is not None else []

# --- サイドバー操作 ---
with st.sidebar:
    st.header("⚙️ 設定")
    if st.button("履歴をリセット", use_container_width=True):
        st.session_state.cc_history = []
        storage.set_item("cc_history", [])
        st.session_state.cc_hand = None
        st.success("履歴を消去しました")
        st.rerun()

    st.write("---")
    # 役の解説（折りたたみ）
    with st.expander("📖 役の強弱解説"):
        st.markdown("""
        1. **ピンゾロ**: 最強
        2. **アラシ**: ゾロ目
        3. **シゴロ**: 4-5-6
        4. **通常の目**: 2つ揃った残りの数
        5. **ブタ**: 役なし
        6. **ヒフミ**: 1-2-3 (最弱)
        """)

# --- メインエリア ---
st.info("サイコロを振って役を判定します。履歴はリセットするまで保持されます。")

col_roll, col_res = st.columns([1, 1])

with col_roll:
    if st.button("🎲 サイコロを振る！", use_container_width=True):
        dice_place = st.empty()
        render_dice_animation(dice_place)

        final_dice = roll_dice(3)
        st.session_state.cc_dice = final_dice
        hand_key = evaluate_hand(final_dice)
        st.session_state.cc_hand = hand_key

        # 履歴に追加
        hand_info = HAND_RANK[hand_key]
        dice_str = " ".join([DICE_EMOJI[d] for d in final_dice])
        new_record = {"time": get_jst_now().strftime("%H:%M:%S"), "dice": dice_str, "hand": hand_info["name"]}
        # 履歴を先頭に追加（新しい順）
        st.session_state.cc_history.insert(0, new_record)
        storage.set_item("cc_history", st.session_state.cc_history)

        dice_place.empty()

    # 現在のサイコロ表示 (背景を少し暗く透過させて、白いサイコロを見やすくする)
    html = f"<div style='text-align: center; background-color: rgba(0, 0, 0, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #ddd;'>{display_dice_html(st.session_state.cc_dice)}</div>"
    st.markdown(html, unsafe_allow_html=True)

with col_res:
    if st.session_state.cc_hand:
        hand_info = HAND_RANK[st.session_state.cc_hand]
        st.markdown("<h3 style='text-align: center;'>最新の結果</h3>", unsafe_allow_html=True)
        st.markdown(
            f"<h2 style='text-align: center; color: #1f77b4;'>役: {hand_info['name']}</h2>", unsafe_allow_html=True
        )
        st.markdown(
            f"<p style='text-align: center; color: gray;'>{hand_info['description']}</p>", unsafe_allow_html=True
        )

        if hand_info["strength"] > 0:
            st.balloons()
        elif hand_info["strength"] < 0:
            st.error("最弱の役です...")
        else:
            st.warning("役なしです。")
    else:
        st.write(" ")
        st.markdown(
            "<h3 style='text-align: center; color: gray; margin-top: 50px;'>サイコロを振ってください</h3>",
            unsafe_allow_html=True,
        )

st.write("---")

# --- 履歴表示エリア ---
st.subheader("📜 出目・役の履歴")
if st.session_state.cc_history:
    # 履歴をテーブルで表示
    history_df = pd.DataFrame(st.session_state.cc_history)
    # カラム名を分かりやすく
    history_df.columns = ["時刻", "サイコロ", "役名"]
    st.table(history_df)
else:
    st.write("履歴はありません。")

# 役の一覧（参考）
with st.expander("📊 役の一覧表（強さ順）"):
    rank_data = []
    for k, v in sorted(HAND_RANK.items(), key=lambda item: item[1]["strength"], reverse=True):
        if "ARASHI" in k and k != "ARASHI_6":
            continue
        if "POINT" in k and k != "POINT_6":
            continue
        name = v["name"]
        if k == "ARASHI_6":
            name = "アラシ (6-6-6 〜 2-2-2)"
        if k == "POINT_6":
            name = "通常の目 (6の目 〜 1の目)"
        rank_data.append(
            {
                "強さ": "↑ 強い" if v["strength"] == 1000 else ("↓ 弱い" if v["strength"] == -100 else "-"),
                "役名": name,
                "解説": v["description"],
            }
        )
    st.table(rank_data)
render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
