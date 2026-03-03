import json

import pandas as pd
import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.slot import (
    calculate_probabilities,
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

st.title(f"🎰 {st.session_state.slot_config.get('name', '標準スロット')}")

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
    def render_slot_machine(initial, target, symbols, trigger, sound, is_win):
        html_template = f"""
        <style>{slot_css}</style>
        <div id="slot-container" class="slot-machine"></div>
        <script>
            {slot_js}
            const config = {{
                initialReels: {json.dumps(initial)},
                targetReels: {json.dumps(target)},
                symbols: {json.dumps(symbols)},
                spinTrigger: {trigger},
                soundEnabled: {json.dumps(sound)},
                isWin: {json.dumps(is_win)}
            }};
            setupSlot(config);
        </script>
        """
        st.components.v1.html(html_template, height=220)

    is_win = st.session_state.slot_result is not None
    render_slot_machine(
        st.session_state.slot_reels,
        st.session_state.slot_target_reels,
        st.session_state.slot_config["symbols"],
        st.session_state.slot_spin_trigger,
        st.session_state.slot_sound_enabled,
        is_win
    )

    if st.button("🔥 レバーを叩く！", use_container_width=True, type="primary"):
        # Python側で先に抽選
        final_reels = spin_reels(st.session_state.slot_config["symbols"])
        result = evaluate_slot_spin(final_reels, st.session_state.slot_config["payouts"])
        
        # 状態更新（表示はJSに任せるが、データは確定させる）
        st.session_state.slot_reels = st.session_state.slot_target_reels # 前回の結果を初期位置に
        st.session_state.slot_target_reels = final_reels
        st.session_state.slot_result = result
        st.session_state.slot_spin_trigger += 1
        st.session_state.slot_spins += 1
        storage.set_item("slot_spins", st.session_state.slot_spins)
        
        # 統計と履歴の更新
        res_name = result["name"] if result else "ハズレ"
        st.session_state.slot_counts[res_name] = st.session_state.slot_counts.get(res_name, 0) + 1
        storage.set_item("slot_counts", st.session_state.slot_counts)
        
        reels_str = " ".join([s["char"] for s in final_reels])
        st.session_state.slot_history.insert(0, {
            "spin": st.session_state.slot_spins,
            "time": get_jst_now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": res_name,
            "reels": reels_str
        })
        storage.set_item("slot_history", st.session_state.slot_history)
        st.rerun()

with col_sub:
    with st.container(border=True):
        # JS演出完了を待つためのディレイを考慮した表示
        container_class = "strictly-delayed" if st.session_state.slot_spin_trigger > 0 else ""
        st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
        
        if st.session_state.slot_result:
            res = st.session_state.slot_result
            st.success(f"🎊 {res['name']} 🎊")
            st.balloons()
        elif st.session_state.slot_history and st.session_state.slot_history[0]["result"] == "ハズレ":
            st.info("残念！もう一回！")
        else:
            st.markdown("<div style='height:150px; display:flex; align-items:center; justify-content:center; color:gray;'>レバーを叩いてね！</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# 強力な遅延表示用 CSS (ルーレットと同様)
st.markdown(
    """
<style>
@keyframes waitThenShow {
    0% { opacity: 0; pointer-events: none; }
    90% { opacity: 0; pointer-events: none; }
    100% { opacity: 1; pointer-events: auto; }
}
.strictly-delayed {
    animation: waitThenShow 3.0s forwards;
}
</style>
""",
    unsafe_allow_html=True,
)

st.write("")
# --- 統計と履歴 ---
tab1, tab2 = st.tabs(["📊 成立統計", "📜 実戦履歴"])

with tab1:
    st.subheader("成立履歴の統計")
    symbols = st.session_state.slot_config["symbols"]
    payouts = st.session_state.slot_config["payouts"]
    total_spins = st.session_state.slot_spins
    probs = calculate_probabilities(symbols, payouts)
    theo_prob_map = {r["name"]: r["denominator"] for r in probs["hit_rates"]}
    
    stats_data = []
    for p in payouts:
        name = p["name"]
        count = st.session_state.slot_counts.get(name, 0)
        theo_denom = theo_prob_map.get(name, 0.0)
        actual_denom = round(total_spins / count, 1) if count > 0 else 0.0
        stats_data.append({
            "役名": name, "回数": count, "理論確率 (1/N)": f"1/{theo_denom}", "実戦確率 (1/N)": f"1/{actual_denom}" if actual_denom > 0 else "---"
        })
    
    miss_count = st.session_state.slot_counts.get("ハズレ", 0)
    actual_miss_rate = (miss_count / total_spins * 100) if total_spins > 0 else 0.0
    stats_data.append({
        "役名": "ハズレ", "回数": miss_count, "理論確率 (1/N)": f"{probs['miss_rate']:.1f}%", "実戦確率 (1/N)": f"{actual_miss_rate:.1f}%"
    })
    st.table(stats_data)

with tab2:
    if st.session_state.slot_history:
        df_hist = pd.DataFrame(st.session_state.slot_history)
        df_hist.columns = ["回転数", "時刻", "成立役", "出目"]
        c1, c2 = st.columns([3, 1])
        with c1: st.write(f"全 {len(df_hist)} 件の履歴")
        with c2:
            csv = df_hist.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 CSVで出力", csv, f"slot_history_{get_jst_now().strftime('%Y%m%d')}.csv", "text/csv")
        st.table(df_hist.head(100))
    else:
        st.write("履歴はありません。")

# サイドバー
with st.sidebar:
    st.header("⚙️ 設定")
    st.session_state.slot_sound_enabled = st.toggle("🔊 サウンドを有効にする", value=st.session_state.slot_sound_enabled)
    if st.button("統計をリセット"):
        st.session_state.slot_spins = 0
        st.session_state.slot_counts = {}
        st.session_state.slot_history = []
        storage.set_item("slot_spins", 0)
        storage.set_item("slot_counts", {})
        storage.set_item("slot_history", [])
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
