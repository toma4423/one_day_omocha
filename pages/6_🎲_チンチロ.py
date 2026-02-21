import streamlit as st
import random
from src.utils.dice import (
    HAND_RANK, roll_dice, evaluate_hand, 
    display_dice_html, render_dice_animation
)

st.set_page_config(page_title="チンチロ", page_icon="🎲")

# --- セッション状態の初期化 ---
if 'cc_dice' not in st.session_state:
    st.session_state.cc_dice = [1, 2, 3]
if 'cc_hand' not in st.session_state:
    st.session_state.cc_hand = None

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
    """)

st.info("サイコロを振って役を判定します。")

# メイン操作エリア
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎲 サイコロを振る！", use_container_width=True):
        dice_place = st.empty()
        render_dice_animation(dice_place)
        
        final_dice = roll_dice(3)
        st.session_state.cc_dice = final_dice
        st.session_state.cc_hand = evaluate_hand(final_dice)
        dice_place.empty()

    # サイコロ表示
    html = f"<div style='text-align: center;'>{display_dice_html(st.session_state.cc_dice)}</div>"
    st.markdown(html, unsafe_allow_html=True)

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
    # 重複表示を避ける
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
