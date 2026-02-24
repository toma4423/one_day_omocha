import json
import time

import pandas as pd
import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.slot import (
    evaluate_slot_spin,
    get_slot_config,
    migrate_slot_config,
    resolve_pattern_to_chars,
    spin_reels,
)
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
    st.session_state.slot_reels = [
        {"char": "7️⃣", "image_url": None},
        {"char": "7️⃣", "image_url": None},
        {"char": "7️⃣", "image_url": None},
    ]
if "slot_history" not in st.session_state:
    saved_history = storage.get_item("slot_history", is_json=True)
    st.session_state.slot_history = saved_history if saved_history else []
if "slot_result" not in st.session_state:
    st.session_state.slot_result = None

# 統計情報の初期化
if "slot_spins" not in st.session_state:
    saved_spins = storage.get_item("slot_spins", is_json=False)
    st.session_state.slot_spins = int(saved_spins) if saved_spins is not None else 0
if "slot_total_score" not in st.session_state:
    saved_total_score = storage.get_item("slot_total_score", is_json=False)
    st.session_state.slot_total_score = int(saved_total_score) if saved_total_score is not None else 0

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

st.title(f"🎰 スロットマシン - {st.session_state.slot_config.get('name', '標準スロット')}")

# 統計情報の表示
c_stat1, c_stat2 = st.columns(2)
with c_stat1:
    st.metric("総回転数", st.session_state.slot_spins)
with c_stat2:
    st.metric("累計スコア", st.session_state.slot_total_score)

# --- メインエリア ---
col1, col2 = st.columns([2, 1])

with col1:
    # リール表示用プレースホルダー
    reel_placeholder = st.empty()

    # 単一の図柄をレンダリングするヘルパー（テキスト or 画像）
    def render_symbol_html(symbol_obj):
        char = symbol_obj["char"]
        url = symbol_obj.get("image_url")
        if url:
            return f'<img src="{url}" style="width: 100px; height: 100px; object-fit: contain;" alt="{char}">'
        return char

    # 現在のリール状態を表示
    def render_reels(reels, spinning=False):
        cls = "reel spin-animation" if spinning else "reel"
        html = f"""
        <div class="reel-container">
            <div class="{cls}">{render_symbol_html(reels[0])}</div>
            <div class="{cls}">{render_symbol_html(reels[1])}</div>
            <div class="{cls}">{render_symbol_html(reels[2])}</div>
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

        # 統計更新
        st.session_state.slot_spins += 1
        storage.set_item("slot_spins", st.session_state.slot_spins)
        if result:
            st.session_state.slot_total_score += result["score"]
            storage.set_item("slot_total_score", st.session_state.slot_total_score)

        # 履歴追加
        res_name = result["name"] if result else "ハズレ"
        new_record = {
            "time": get_jst_now().strftime("%H:%M:%S"),
            "result": res_name,
        }
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
        df.columns = ["時刻", "成立役"]
        st.table(df)
    else:
        st.write("履歴はありません。")

with col_info:
    st.subheader("📊 役の一覧")
    payout_data = []
    symbols = st.session_state.slot_config["symbols"]

    for p in st.session_state.slot_config["payouts"]:
        char_pattern = resolve_pattern_to_chars(p["pattern"], symbols)
        payout_data.append({"役名": p["name"], "パターン": " ".join(char_pattern), "スコア": p["score"]})
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
                    migrated_config = migrate_slot_config(data_load)
                    st.session_state.slot_config = migrated_config
                    storage.set_item("slot_config", migrated_config)
                    if "slot_config_edit" in st.session_state:
                        st.session_state.slot_config_edit = migrated_config
                    st.success("設定を反映しました！")
                    st.rerun()
                else:
                    st.error("不正な設定ファイル形式です")
            except Exception:
                st.error("JSONの読み込みに失敗しました")

    st.write("---")

    if st.button("統計をリセット"):
        st.session_state.slot_spins = 0
        st.session_state.slot_total_score = 0
        storage.set_item("slot_spins", 0)
        storage.set_item("slot_total_score", 0)
        st.success("統計をリセットしました")
        st.rerun()

    if st.button("履歴をクリア"):
        st.session_state.slot_history = []
        storage.set_item("slot_history", [])
        st.success("クリアしました")
        st.rerun()

    st.info("設定は「スロット作成」ページから変更できます。")

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
