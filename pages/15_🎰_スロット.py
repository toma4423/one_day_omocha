import json

import pandas as pd
import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.slot import (
    SlotConfig,
    evaluate_slot_spin,
    get_slot_config,
    spin_reels,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header
from src.utils.time import get_jst_now

st.set_page_config(page_title="スロット", page_icon="🎰", layout="wide")

# グローバルスタイルの適用
render_page_header()

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# 設定のロード
if "slot_config" not in st.session_state:
    saved_config = storage.get_item("slot_config", is_json=True)
    st.session_state.slot_config = get_slot_config(saved_config)

# セッション状態の初期化
if "slot_reels" not in st.session_state:
    st.session_state.slot_reels = [{"char": "7️⃣", "image_url": None}] * 3
if "slot_history" not in st.session_state:
    saved_history = storage.get_item("slot_history", is_json=True)
    st.session_state.slot_history = saved_history if saved_history else []
if "slot_result" not in st.session_state:
    st.session_state.slot_result = None
if "slot_spins" not in st.session_state:
    saved_spins = storage.get_item("slot_spins", is_json=False)
    st.session_state.slot_spins = int(saved_spins) if saved_spins is not None else 0
if "slot_counts" not in st.session_state:
    saved_counts = storage.get_item("slot_counts", is_json=True)
    st.session_state.slot_counts = saved_counts if saved_counts else {}
if "slot_sound_enabled" not in st.session_state:
    st.session_state.slot_sound_enabled = True

# JS演出用のトリガー
if "slot_spin_trigger" not in st.session_state:
    st.session_state.slot_spin_trigger = 0
if "slot_target_reels" not in st.session_state:
    st.session_state.slot_target_reels = st.session_state.slot_reels

# Pydanticモデルから値を取得
config: SlotConfig = st.session_state.slot_config
st.title(f"🎰 {config.name}")

# 回転数の表示
with st.container(border=True):
    st.metric("総回転数", f"{st.session_state.slot_spins} 回")

st.write("")

# --- メインエリア ---
col_main, col_sub = st.columns([2, 1])

with col_main:
    # 外部 JS/CSS の読み込み
    try:
        with open("src/assets/slot/reel.js", encoding="utf-8") as f:
            slot_js = f.read()
        with open("src/assets/slot/style.css", encoding="utf-8") as f:
            slot_css = f.read()
    except Exception as e:
        slot_js = f"console.error('{e}')"
        slot_css = ""

    # JSコンポーネントのレンダリング
    def render_slot_machine(initial, target, symbols, trigger, sound, result):
        is_win = result is not None
        win_name = result.name if is_win else ""

        # モデルをシリアライズ可能な形式に変換
        symbols_data = [s.model_dump() for s in symbols]

        html_template = f"""
        <style>{slot_css}</style>
        <div id="slot-container" class="slot-machine"></div>
        <script>
            {slot_js}
            const config = {{
                initialReels: {json.dumps(initial)},
                targetReels: {json.dumps(target)},
                symbols: {json.dumps(symbols_data)},
                spinTrigger: {trigger},
                soundEnabled: {json.dumps(sound)},
                isWin: {json.dumps(is_win)},
                winName: {json.dumps(win_name)}
            }};
            setupSlot(config);
        </script>
        """
        st.components.v1.html(html_template, height=250)

    render_slot_machine(
        st.session_state.slot_reels,
        st.session_state.slot_target_reels,
        config.symbols,
        st.session_state.slot_spin_trigger,
        st.session_state.slot_sound_enabled,
        st.session_state.slot_result,
    )

    if st.button("🔥 レバーを叩く！", use_container_width=True, type="primary"):
        # Python側で先に抽選
        final_reels = spin_reels(config)
        result = evaluate_slot_spin(final_reels, config.payouts)

        # 状態更新 (JSに渡すため dict に変換)
        final_reels_data = [s.model_dump() for s in final_reels]
        st.session_state.slot_reels = st.session_state.slot_target_reels
        st.session_state.slot_target_reels = final_reels_data
        st.session_state.slot_result = result
        st.session_state.slot_spin_trigger += 1
        st.session_state.slot_spins += 1
        storage.set_item("slot_spins", st.session_state.slot_spins)

        # 統計と履歴の更新
        res_name = result.name if result else "ハズレ"
        st.session_state.slot_counts[res_name] = st.session_state.slot_counts.get(res_name, 0) + 1
        storage.set_item("slot_counts", st.session_state.slot_counts)

        reels_str = " ".join([s.char for s in final_reels])
        st.session_state.slot_history.insert(
            0,
            {
                "spin": st.session_state.slot_spins,
                "time": get_jst_now().strftime("%Y-%m-%d %H:%M:%S"),
                "result": res_name,
                "reels": reels_str,
            },
        )
        storage.set_item("slot_history", st.session_state.slot_history)
        st.rerun()

with col_sub:
    with st.container(border=True):
        st.markdown(
            "<div style='height:180px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#555;'>"
            "<h3 style='margin-bottom:10px;'>🎮 遊び方</h3>"
            "<p style='margin:2px 0;'>1. レバーを叩く</p>"
            "<p style='margin:2px 0;'>2. リールが自動で停止</p>"
            "<p style='margin:2px 0;'>3. 揃えば当たり！</p>"
            "<p style='margin-top:15px; font-size:0.8em; color:gray;'>※ 結果はリール上に表示されます</p>"
            "</div>",
            unsafe_allow_html=True,
        )

st.write("")
# --- 統計と履歴 ---
tab1, tab2 = st.tabs(["📊 成立統計", "📜 実戦履歴"])

with tab1:
    st.subheader("成立履歴の統計")
    total_spins = st.session_state.slot_spins

    stats_data = []
    # 役ごとの統計
    for p in config.payouts:
        name = p.name
        count = st.session_state.slot_counts.get(name, 0)
        denom = p.denominator if p.denominator > 0 else "??"

        stats_data.append({"役名": name, "回数": count, "確率 (1/N)": f"1/{denom}"})

    # ハズレの統計
    miss_count = st.session_state.slot_counts.get("ハズレ", 0)
    stats_data.append({"役名": "ハズレ", "回数": miss_count, "確率 (1/N)": "---"})

    st.table(stats_data)
    st.caption(f"現在の設定「{config.name}」に基づいた集計結果です。")

with tab2:
    if st.session_state.slot_history:
        df_hist = pd.DataFrame(st.session_state.slot_history)
        df_hist.columns = ["回転数", "時刻", "成立役", "出目"]
        c1, c2 = st.columns([3, 1])
        with c1:
            st.write(f"全 {len(df_hist)} 件の履歴")
        with c2:
            csv = df_hist.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 CSVで出力", csv, f"slot_history_{get_jst_now().strftime('%Y%m%d')}.csv", "text/csv")
        st.table(df_hist.head(100))
    else:
        st.write("履歴はありません。")

# サイドバー
with st.sidebar:
    st.header("⚙️ 設定")
    st.session_state.slot_sound_enabled = st.toggle(
        "🔊 サウンドを有効にする", value=st.session_state.slot_sound_enabled
    )

    st.write("---")
    st.subheader("📥 設定の読み込み")
    uploaded_file = st.file_uploader("設定JSONを読み込む", type="json")
    if uploaded_file and st.button("設定を反映", use_container_width=True, type="primary"):
        try:
            from src.utils.slot import validate_slot_config

            data = json.load(uploaded_file)
            valid, msg = validate_slot_config(data)
            if valid:
                new_config = SlotConfig(**data)
                st.session_state.slot_config = new_config
                storage.set_item("slot_config", new_config.model_dump())
                st.success(f"✅ 設定「{new_config.name}」を反映しました！")
                st.balloons()
                st.rerun()
            else:
                st.error(msg)
        except Exception as e:
            st.error(f"読込失敗: {e}")

    st.write("---")
    if st.button("統計をリセット"):
        st.session_state.slot_spins = 0
        st.session_state.slot_counts = {}
        st.session_state.slot_history = []
        storage.set_item("slot_spins", 0)
        storage.set_item("slot_counts", {})
        storage.set_item("slot_history", [])
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
