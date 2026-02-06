import streamlit as st
import random
import time

st.set_page_config(page_title="チンチロ", page_icon="🎲")

# --- 定数と役の定義 ---
HAND_RANK = {
    "PINZORO": {"name": "ピンゾロ (1-1-1)", "score": 100, "multiplier": 5},
    "ARASHI": {"name": "アラシ (ゾロ目)", "score": 50, "multiplier": 3},
    "SHIGORO": {"name": "シゴロ (4-5-6)", "score": 40, "multiplier": 2},
    "POINT_6": {"name": "6の目", "score": 6, "multiplier": 1},
    "POINT_5": {"name": "5の目", "score": 5, "multiplier": 1},
    "POINT_4": {"name": "4の目", "score": 4, "multiplier": 1},
    "POINT_3": {"name": "3の目", "score": 3, "multiplier": 1},
    "POINT_2": {"name": "2の目", "score": 2, "multiplier": 1},
    "POINT_1": {"name": "1の目", "score": 1, "multiplier": 1},
    "BUTA": {"name": "ブタ (役なし)", "score": 0, "multiplier": 1},
    "HIFUMI": {"name": "ヒフミ (1-2-3)", "score": -1, "multiplier": 2}, # 負け確定、倍払い
}

def evaluate_hand(dice):
    dice.sort()
    d1, d2, d3 = dice[0], dice[1], dice[2]
    
    if d1 == 1 and d2 == 1 and d3 == 1:
        return "PINZORO", d1
    if d1 == d2 == d3:
        return "ARASHI", d1
    if d1 == 4 and d2 == 5 and d3 == 6:
        return "SHIGORO", 0
    if d1 == 1 and d2 == 2 and d3 == 3:
        return "HIFUMI", 0
    
    # 目の判定
    if d1 == d2:
        return f"POINT_{d3}", d3
    if d2 == d3:
        return f"POINT_{d1}", d1
    if d1 == d3: # ソート済みなのでありえないが念のため
        return f"POINT_{d2}", d2
        
    return "BUTA", 0

# --- セッション状態の初期化 ---
if 'cc_money' not in st.session_state: st.session_state.cc_money = 1000
if 'cc_state' not in st.session_state: st.session_state.cc_state = "betting" # betting, dealer_rolling, player_rolling, result
if 'cc_bet' not in st.session_state: st.session_state.cc_bet = 100
if 'cc_dealer_hand' not in st.session_state: st.session_state.cc_dealer_hand = None
if 'cc_player_hand' not in st.session_state: st.session_state.cc_player_hand = None
if 'cc_messages' not in st.session_state: st.session_state.cc_messages = []
if 'cc_roll_count' not in st.session_state: st.session_state.cc_roll_count = 0

def add_msg(msg):
    st.session_state.cc_messages.append(msg)

def reset_game():
    st.session_state.cc_state = "betting"
    st.session_state.cc_dealer_hand = None
    st.session_state.cc_player_hand = None
    st.session_state.cc_messages = []
    st.session_state.cc_roll_count = 0

# --- UI構築 ---
st.title("🎲 チンチロリン")

# ルール説明
with st.expander("📜 ルールと役の強さ"):
    st.markdown("""
    **基本ルール**
    親（COM）と子（あなた）でサイコロを3つ振り、役の強さを競います。
    持ち点は1000点からスタートです。
    
    **ゲームの流れ**
    1. **親（COM）が振る**: 最大3回まで。役が出たらそこで確定。
       - **即勝利**: ピンゾロ、アラシ、シゴロが出た場合、親の勝利で終了。
       - **即負け**: ヒフミが出た場合、親の負け（支払い発生）。ブタ（3回役なし）も親の負け。
       - **目（ポイント）**: 目が出た場合、子のターンへ。
    2. **子（あなた）が振る**: 親が目を出した場合のみ。最大3回まで。
       - 役が出たら親と比較して勝敗決定。
       - ブタ（3回役なし）は負け。
    
    **役の強さ（強い順）**
    1. **ピンゾロ (1-1-1)**: 最強。賭け金の5倍。
    2. **アラシ (2-2-2 〜 6-6-6)**: 賭け金の3倍。
    3. **シゴロ (4-5-6)**: 賭け金の2倍。
    4. **目 (6 > 5 > ... > 1)**: 同じ目が2つある時の、残りの数字。大きいほど強い。賭け金1倍。
    5. **ブタ (役なし)**: 最弱。
    6. **ヒフミ (1-2-3)**: 即負け。賭け金の2倍支払い。
    """)

# ステータス表示
st.markdown(f"### 💰 所持金: {st.session_state.cc_money}")

# --- ゲームロジック ---

# 1. ベット画面
if st.session_state.cc_state == "betting":
    st.info("賭け金を決めて勝負開始！")
    bet = st.number_input("賭け金", min_value=1, max_value=st.session_state.cc_money, value=min(100, st.session_state.cc_money), step=10)
    
    if st.button("勝負する！", use_container_width=True):
        st.session_state.cc_bet = bet
        st.session_state.cc_state = "dealer_rolling"
        st.session_state.cc_roll_count = 0
        add_msg(f"🚩 勝負開始！ 賭け金: {bet}")
        st.rerun()

# 2. 親（COM）のターン
elif st.session_state.cc_state == "dealer_rolling":
    st.subheader("🤖 親（COM）のターン")
    
    if st.button("親がサイコロを振る", use_container_width=True):
        dice = [random.randint(1, 6) for _ in range(3)]
        hand_key, point = evaluate_hand(dice)
        hand_info = HAND_RANK[hand_key]
        
        st.session_state.cc_roll_count += 1
        roll_msg = f"親の{st.session_state.cc_roll_count}回目の出目: {dice} -> {hand_info['name']}"
        add_msg(roll_msg)
        
        # 役確定判定
        is_finish = False
        dealer_win = False
        player_win = False
        multiplier = hand_info['multiplier']
        
        if hand_key in ["PINZORO", "ARASHI", "SHIGORO"]:
            # 親の即勝利
            add_msg(f"🔥 親が **{hand_info['name']}** を出しました！ 親の勝利です。")
            st.session_state.cc_dealer_hand = {"dice": dice, "key": hand_key, "score": hand_info['score'], "multi": multiplier}
            dealer_win = True
            is_finish = True
            
        elif hand_key == "HIFUMI":
            # 親の即負け
            add_msg(f"📉 親が **{hand_info['name']}** を出しました... あなたの勝ちです！")
            st.session_state.cc_dealer_hand = {"dice": dice, "key": hand_key, "score": hand_info['score'], "multi": multiplier}
            player_win = True
            is_finish = True
            
        elif "POINT" in hand_key:
            # 目が確定
            add_msg(f"✅ 親の目が **{hand_info['name']}** に確定しました。あなたの番です。")
            st.session_state.cc_dealer_hand = {"dice": dice, "key": hand_key, "score": hand_info['score'], "multi": multiplier}
            st.session_state.cc_state = "player_rolling"
            st.session_state.cc_roll_count = 0 # 子のカウントリセット
            st.rerun()
            
        elif hand_key == "BUTA":
            if st.session_state.cc_roll_count >= 3:
                # 親が3回ブタ
                add_msg("💨 親は3回振って役なし（ブタ）でした。あなたの勝ちです！")
                st.session_state.cc_dealer_hand = {"dice": dice, "key": hand_key, "score": hand_info['score'], "multi": 1}
                player_win = True
                is_finish = True
            else:
                add_msg("親は役が出なかったので振り直します...")
        
        if is_finish:
            st.session_state.cc_state = "result"
            if dealer_win:
                amount = st.session_state.cc_bet * multiplier
                st.session_state.cc_money -= amount
                add_msg(f"💸 {amount} の没収...")
            elif player_win:
                amount = st.session_state.cc_bet * multiplier
                st.session_state.cc_money += amount
                add_msg(f"🎉 {amount} を獲得！")
            st.rerun()

# 3. 子（プレイヤー）のターン
elif st.session_state.cc_state == "player_rolling":
    st.subheader("👤 あなたのターン")
    st.info(f"親の目: {HAND_RANK[st.session_state.cc_dealer_hand['key']]['name']}")
    
    if st.button("サイコロを振る！", use_container_width=True):
        dice = [random.randint(1, 6) for _ in range(3)]
        hand_key, point = evaluate_hand(dice)
        hand_info = HAND_RANK[hand_key]
        
        st.session_state.cc_roll_count += 1
        roll_msg = f"あなたの{st.session_state.cc_roll_count}回目の出目: {dice} -> {hand_info['name']}"
        add_msg(roll_msg)
        
        is_finish = False
        player_win = False
        dealer_win = False
        draw = False
        # 子の倍率は自分の役依存（ピンゾロなど）か、親との勝負（通常1倍）か
        # 一般的には子の特殊役が出ればその倍率取り。目が勝てば1倍。
        
        final_multi = 1
        
        if hand_key in ["PINZORO", "ARASHI", "SHIGORO"]:
            add_msg(f"🔥 **{hand_info['name']}**！！ あなたの勝利です！")
            final_multi = hand_info['multiplier']
            player_win = True
            is_finish = True
            
        elif hand_key == "HIFUMI":
            add_msg(f"😱 **{hand_info['name']}**... あなたの負けです。")
            final_multi = hand_info['multiplier']
            dealer_win = True
            is_finish = True
            
        elif "POINT" in hand_key:
            player_score = hand_info['score']
            dealer_score = st.session_state.cc_dealer_hand['score']
            
            add_msg(f"目が **{hand_info['name']}** になりました。勝負！")
            
            if player_score > dealer_score:
                add_msg(f"勝ち！ ({player_score} > {dealer_score})")
                player_win = True
            elif player_score < dealer_score:
                add_msg(f"負け... ({player_score} < {dealer_score})")
                dealer_win = True
            else:
                add_msg(f"引き分け ({player_score} = {dealer_score})")
                draw = True
            is_finish = True
            
        elif hand_key == "BUTA":
            if st.session_state.cc_roll_count >= 3:
                add_msg("💨 3回振って役なし（ブタ）... あなたの負けです。")
                dealer_win = True
                is_finish = True
        
        if is_finish:
            st.session_state.cc_state = "result"
            if player_win:
                amount = st.session_state.cc_bet * final_multi
                st.session_state.cc_money += amount
                add_msg(f"🎉 {amount} を獲得！")
            elif dealer_win:
                amount = st.session_state.cc_bet * final_multi
                st.session_state.cc_money -= amount
                add_msg(f"💸 {amount} の没収...")
            elif draw:
                add_msg("🤝 引き分け。賭け金が戻ります。")
            st.rerun()

# 4. 結果画面
elif st.session_state.cc_state == "result":
    st.subheader("結果発表")
    
    if st.button("もう一度遊ぶ", use_container_width=True):
        if st.session_state.cc_money <= 0:
            st.error("所持金がなくなりました... ゲームオーバー")
            if st.button("1000円借りてリセット"):
                st.session_state.cc_money = 1000
                reset_game()
                st.rerun()
        else:
            reset_game()
            st.rerun()

# ログ表示
st.write("---")
st.subheader("📝 行動ログ")
for msg in reversed(st.session_state.cc_messages):
    st.caption(msg)
