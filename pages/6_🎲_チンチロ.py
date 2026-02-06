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

# 役の定義と強さ（数値が高いほど強い）
HAND_RANK = {
    "PINZORO": {"name": "ピンゾロ (1-1-1)", "strength": 1000, "description": "最強の役。"},
    "ARASHI_6": {"name": "アラシ (6-6-6)", "strength": 606, "description": "ゾロ目。数字が大きいほど強い。"},
    "ARASHI_5": {"name": "アラシ (5-5-5)", "strength": 605, "description": "ゾロ目。"},
    "ARASHI_4": {"name": "アラシ (4-4-4)", "strength": 604, "description": "ゾロ目。"},
    "ARASHI_3": {"name": "アラシ (3-3-3)", "strength": 603, "description": "ゾロ目。"},
    "ARASHI_2": {"name": "アラシ (2-2-2)", "strength": 602, "description": "ゾロ目。"},
    "SHIGORO": {"name": "シゴロ (4-5-6)", "strength": 500, "description": "4-5-6の連番。非常に強い。"},
    "POINT_6": {"name": "6の目", "strength": 6, "description": "2つのサイコロが揃い、残りが6。"},
    "POINT_5": {"name": "5の目", "strength": 5, "description": "2つのサイコロが揃い、残りが5。"},
    "POINT_4": {"name": "4の目", "strength": 4, "description": "2つのサイコロが揃い、残りが4。"},
    "POINT_3": {"name": "3の目", "strength": 3, "description": "2つのサイコロが揃い、残りが3。"},
    "POINT_2": {"name": "2の目", "strength": 2, "description": "2つのサイコロが揃い、残りが2。"},
    "POINT_1": {"name": "1の目", "strength": 1, "description": "2つのサイコロが揃い、残りが1。"},
    "BUTA": {"name": "ブタ (役なし)", "strength": 0, "description": "役が成立していない状態。"},
    "HIFUMI": {"name": "ヒフミ (1-2-3)", "strength": -100, "description": "最低の役。即負け。"},
}

def evaluate_hand(dice):
    dice.sort()
    d1, d2, d3 = dice[0], dice[1], dice[2]
    
    # ピンゾロ
    if d1 == 1 and d2 == 1 and d3 == 1:
        return "PINZORO"
    
    # アラシ
    if d1 == d2 == d3:
        return f"ARASHI_{d1}"
    
    # シゴロ
    if d1 == 4 and d2 == 5 and d3 == 6:
        return "SHIGORO"
    
    # ヒフミ
    if d1 == 1 and d2 == 2 and d3 == 3:
        return "HIFUMI"
    
    # 目（ポイント）
    # ソートされているので d1=d2 か d2=d3 のどちらか
    if d1 == d2:
        return f"POINT_{d3}"
    if d2 == d3:
        return f"POINT_{d1}"
        
    return "BUTA"

def display_dice(dice):
    dice_html = "".join([f"<span style='font-size: 100px; margin: 0 10px;'>{DICE_EMOJI[d]}</span>" for d in dice])
    st.markdown(f"<div style='text-align: center;'>{dice_html}</div>", unsafe_allow_html=True)

# --- セッション状態の初期化 ---
if 'cc_dice' not in st.session_state: st.session_state.cc_dice = [1, 2, 3]
if 'cc_hand' not in st.session_state: st.session_state.cc_hand = None

# --- UI構築 ---
st.title("🎲 チンチロリン")

# 強弱の解説
with st.expander("📖 役の強弱とルールの解説"):
    st.markdown("""
    ### 役の強さ順
    1. **ピンゾロ (1-1-1)**: 最強。
    2. **アラシ (ゾロ目)**: 数字が大きいほど強い (6-6-6 > 2-2-2)。
    3. **シゴロ (4-5-6)**: 非常に強い。
    4. **通常の目 (6の目 > ... > 1の目)**: 2つ揃った残りの1つの数字で決まります。
    5. **ブタ (役なし)**: 3回振っても役が出ない場合など。
    6. **ヒフミ (1-2-3)**: 最弱。即負け。

    ### 【重要】同じ「目」の場合の強弱
    インターネットの調査によると、一般的なルールでは**「揃ったペアの数字」は強さに影響しません。**
    
    *   例：`2-2-3` (3の目) と `5-5-3` (3の目) が対戦した場合
    *   結果：**引き分け（ドロー）**
    
    あくまで「残りの1つの数字（目）」のみで勝敗を判定するのが標準的なルールです。
    """)

st.info("サイコロを振って役を判定します。")

# メイン操作エリア
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎲 サイコロを振る！", use_container_width=True):
        dice_place = st.empty()
        for _ in range(10):
            temp_dice = [random.randint(1, 6) for _ in range(3)]
            dice_html = "".join([f"<span style='font-size: 100px; margin: 0 10px;'>{DICE_EMOJI[d]}</span>" for d in temp_dice])
            dice_place.markdown(f"<div style='text-align: center;'>{dice_html}</div>", unsafe_allow_html=True)
            time.sleep(0.05)
        
        final_dice = [random.randint(1, 6) for _ in range(3)]
        st.session_state.cc_dice = final_dice
        st.session_state.cc_hand = evaluate_hand(final_dice)
        dice_place.empty()

    display_dice(st.session_state.cc_dice)

# 結果表示
if st.session_state.cc_hand:
    hand_info = HAND_RANK[st.session_state.cc_hand]
    st.markdown("---")
    st.markdown(f"<h2 style='text-align: center;'>役: {hand_info['name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{hand_info['description']}</p>", unsafe_allow_html=True)
    
    if hand_info['strength'] > 0:
        st.balloons()
    elif hand_info['strength'] < 0:
        st.error("最弱の役です...")
    else:
        st.warning("役なしです。")

# 役の一覧表
st.markdown("### 役の一覧表（強さ順）")
rank_data = []
for k, v in sorted(HAND_RANK.items(), key=lambda item: item[1]['strength'], reverse=True):
    # アラシなどは代表して一つ表示
    if "ARASHI" in k and k != "ARASHI_6": continue
    if "POINT" in k and k != "POINT_6": continue
    
    name = v["name"]
    if k == "ARASHI_6": name = "アラシ (6-6-6 〜 2-2-2)"
    if k == "POINT_6": name = "通常の目 (6の目 〜 1の目)"
    
    rank_data.append({
        "強さ": "↑ 強い" if v['strength'] == 1000 else ("↓ 弱い" if v['strength'] == -100 else "-"),
        "役名": name,
        "解説": v["description"]
    })
st.table(rank_data)
