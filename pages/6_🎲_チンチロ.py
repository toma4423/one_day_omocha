import streamlit as st
import random
import time

st.set_page_config(page_title="チンチロ", page_icon="🎲")

# --- 定数と役の定義 ---
DICE_EMOJI = {
    1: "⚀",
    2: "⚁",
    3: "⚂",
    4: "⚃",
    5: "⚄",
    6: "⚅"
}

HAND_RANK = {
    "PINZORO": {"name": "ピンゾロ (1-1-1)", "multiplier": "5倍"},
    "ARASHI": {"name": "アラシ (ゾロ目)", "multiplier": "3倍"},
    "SHIGORO": {"name": "シゴロ (4-5-6)", "multiplier": "2倍"},
    "POINT_6": {"name": "6の目", "multiplier": "1倍"},
    "POINT_5": {"name": "5の目", "multiplier": "1倍"},
    "POINT_4": {"name": "4の目", "multiplier": "1倍"},
    "POINT_3": {"name": "3の目", "multiplier": "1倍"},
    "POINT_2": {"name": "2の目", "multiplier": "1倍"},
    "POINT_1": {"name": "1の目", "multiplier": "1倍"},
    "BUTA": {"name": "ブタ (役なし)", "multiplier": "-"},
    "HIFUMI": {"name": "ヒフミ (1-2-3)", "multiplier": "2倍払い"},
}

def evaluate_hand(dice):
    dice.sort()
    d1, d2, d3 = dice[0], dice[1], dice[2]
    
    if d1 == 1 and d2 == 1 and d3 == 1:
        return "PINZORO"
    if d1 == d2 == d3:
        return "ARASHI"
    if d1 == 4 and d2 == 5 and d3 == 6:
        return "SHIGORO"
    if d1 == 1 and d2 == 2 and d3 == 3:
        return "HIFUMI"
    
    if d1 == d2:
        return f"POINT_{d3}"
    if d2 == d3:
        return f"POINT_{d1}"
    if d1 == d3:
        return f"POINT_{d2}"
        
    return "BUTA"

def display_dice(dice):
    dice_html = "".join([f"<span style='font-size: 100px; margin: 0 10px;'>{DICE_EMOJI[d]}</span>" for d in dice])
    st.markdown(f"<div style='text-align: center;'>{dice_html}</div>", unsafe_allow_html=True)

# --- セッション状態の初期化 ---
if 'cc_dice' not in st.session_state: st.session_state.cc_dice = [1, 2, 3]
if 'cc_hand' not in st.session_state: st.session_state.cc_hand = None

# --- UI構築 ---
st.title("🎲 チンチロリン")

st.info("サイコロを振って役を判定します。")

# メイン操作エリア
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎲 サイコロを振る！", use_container_width=True):
        # 演出用のプレースホルダー
        dice_place = st.empty()
        for _ in range(10):
            temp_dice = [random.randint(1, 6) for _ in range(3)]
            dice_html = "".join([f"<span style='font-size: 100px; margin: 0 10px;'>{DICE_EMOJI[d]}</span>" for d in temp_dice])
            dice_place.markdown(f"<div style='text-align: center;'>{dice_html}</div>", unsafe_allow_html=True)
            time.sleep(0.05)
        
        final_dice = [random.randint(1, 6) for _ in range(3)]
        st.session_state.cc_dice = final_dice
        st.session_state.cc_hand = evaluate_hand(final_dice)
        dice_place.empty() # 演出用を消す

    # 最終的な出目の表示
    display_dice(st.session_state.cc_dice)

# 結果表示
if st.session_state.cc_hand:
    hand_info = HAND_RANK[st.session_state.cc_hand]
    st.markdown("---")
    st.markdown(f"<h2 style='text-align: center;'>役: {hand_info['name']}</h2>", unsafe_allow_html=True)
    if st.session_state.cc_hand != "BUTA":
        st.balloons()
    else:
        st.warning("役なし（ブタ）です。")

# ルール説明
with st.expander("📜 役の一覧"):
    st.table([{"役名": v["name"], "倍率": v["multiplier"]} for k, v in HAND_RANK.items()])