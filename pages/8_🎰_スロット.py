import json
import time

import pandas as pd
import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.slot import evaluate_slot_spin, get_slot_config, spin_reels
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box
from src.utils.time import get_jst_now

st.set_page_config(page_title="スロット", page_icon="🎰", layout="wide")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# 設定のロード
if "slot_config" not in st.session_state:
    saved_config = storage.get_item("slot_config", is_json=True)
    st.session_state.slot_config = get_slot_config(saved_config)

# セッション状態の初期化
if "slot_reels" not in st.session_state:
    st.session_state.slot_reels = ["7️⃣", "7️⃣", "7️⃣"]
if "slot_history" not in st.session_state:
    saved_history = storage.get_item("slot_history", is_json=True)
    st.session_state.slot_history = saved_history if saved_history else []
if "slot_result" not in st.session_state:
    st.session_state.slot_result = None

# CSSによるリールアニメーション風の表示
st.markdown(
    """
    <style>
    .reel-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 40px 0;
    }
    .reel {
        width: 120px;
        height: 120px;
        background: #fdfdfd;
        border: 4px solid #333;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 60px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.2);
    }
    .spin-animation {
        animation: spin 0.1s infinite linear;
    }
    @keyframes spin {
        0% { transform: translateY(0); opacity: 0.5; }
        50% { transform: translateY(-10px); opacity: 0.8; }
        100% { transform: translateY(0); opacity: 0.5; }
    }
    .stButton > button {
        height: 80px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border-radius: 40px !important;
        background-color: #ff4b4b !important;
        color: white !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎰 スロットマシン")

# --- メインエリア ---
col1, col2 = st.columns([2, 1])

with col1:
    # リール表示用プレースホルダー
    reel_placeholder = st.empty()

    # 現在のリール状態を表示
    def render_reels(reels, spinning=False):
        cls = "reel spin-animation" if spinning else "reel"
        html = f"""
        <div class="reel-container">
            <div class="{cls}">{reels[0]}</div>
            <div class="{cls}">{reels[1]}</div>
            <div class="{cls}">{reels[2]}</div>
        </div>
        """
        reel_placeholder.markdown(html, unsafe_allow_html=True)

    render_reels(st.session_state.slot_reels)

    if st.button("🔥 レバーを叩く！", use_container_width=True):
        # アニメーション
        for _ in range(10):
            temp_reels = spin_reels(st.session_state.slot_config["symbols"])
            render_reels(temp_reels, spinning=True)
            time.sleep(0.05)

        # 最終結果
        final_reels = spin_reels(st.session_state.slot_config["symbols"])
        st.session_state.slot_reels = final_reels
        render_reels(final_reels)

        # 判定
        result = evaluate_slot_spin(final_reels, st.session_state.slot_config["payouts"])
        st.session_state.slot_result = result

        # 履歴追加
        res_name = result["name"] if result else "ハズレ"
        new_record = {"time": get_jst_now().strftime("%H:%M:%S"), "reels": " ".join(final_reels), "result": res_name}
        st.session_state.slot_history.insert(0, new_record)
        # 履歴は直近50件
        st.session_state.slot_history = st.session_state.slot_history[:50]
        storage.set_item("slot_history", st.session_state.slot_history)

        st.rerun()

with col2:
    if st.session_state.slot_result:
        res = st.session_state.slot_result
        st.success(f"🎊 {res['name']} 🎊")
        st.markdown(f"<h1 style='text-align:center; color:#ff4b4b;'>+{res['score']}</h1>", unsafe_allow_html=True)
        st.balloons()
    elif (
        st.session_state.slot_result is None
        and "slot_history" in st.session_state
        and len(st.session_state.slot_history) > 0
    ):
        # 直近がハズレの場合
        if st.session_state.slot_history[0]["result"] == "ハズレ":
            st.info("残念！もう一回！")

st.write("---")

# --- 下部エリア ---
col_hist, col_info = st.columns([1, 1])

with col_hist:
    st.subheader("📜 履歴")
    if st.session_state.slot_history:
        df = pd.DataFrame(st.session_state.slot_history)
        df.columns = ["時刻", "出目", "結果"]
        st.table(df)
    else:
        st.write("履歴はありません。")

with col_info:
    st.subheader("📊 役の一覧")
    payout_data = []
    for p in st.session_state.slot_config["payouts"]:
        payout_data.append({"役名": p["name"], "パターン": " ".join(p["pattern"]), "スコア": p["score"]})
    st.table(payout_data)

with st.sidebar:
    st.header("⚙️ オプション")

    # JSONロード
    uploaded_file = st.file_uploader("設定JSONを読込", type="json")
    if uploaded_file is not None:
        if st.button("設定を反映する", use_container_width=True):
            try:
                data_load = json.load(uploaded_file)
                if "symbols" in data_load and "payouts" in data_load:
                    st.session_state.slot_config = data_load
                    storage.set_item("slot_config", data_load)
                    if "slot_config_edit" in st.session_state:
                        st.session_state.slot_config_edit = data_load
                    st.success("設定を反映しました！")
                    st.rerun()
                else:
                    st.error("不正な設定ファイル形式です")
            except Exception:
                st.error("JSONの読み込みに失敗しました")

    st.write("---")

    if st.button("履歴をクリア"):
        st.session_state.slot_history = []
        storage.set_item("slot_history", [])
        st.success("クリアしました")
        st.rerun()

    st.info("設定は「スロット作成」ページから変更できます。")

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
