import json
import random
import time

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.roulette import (
    migrate_roulette_config,
    normalize_weights,
    pick_roulette_winner,
    validate_roulette_config,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header

# ページ基本設定
st.set_page_config(page_title="ルーレット", page_icon="🎡", layout="wide")

# グローバルスタイルの適用
render_page_header()

# 結果と履歴を遅らせるための CSS
st.markdown(
    """
<style>
@keyframes delayedReveal {
    0% { opacity: 0; filter: blur(5px); pointer-events: none; }
    95% { opacity: 0; filter: blur(5px); pointer-events: none; }
    100% { opacity: 1; filter: blur(0); pointer-events: auto; }
}
.reveal-area {
    animation: delayedReveal 4.8s forwards;
}
</style>
""",
    unsafe_allow_html=True,
)

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "roulette_config" not in st.session_state:
    saved_config = storage.get_item("roulette_config", is_json=True)
    st.session_state.roulette_config = migrate_roulette_config(saved_config)

if "roulette_history" not in st.session_state:
    saved_history = storage.get_item("roulette_history", is_json=True)
    st.session_state.roulette_history = saved_history if saved_history else []

if "roulette_last_winner" not in st.session_state:
    st.session_state.roulette_last_winner = None
if "roulette_spin_trigger" not in st.session_state:
    st.session_state.roulette_spin_trigger = 0
if "roulette_winner_index" not in st.session_state:
    st.session_state.roulette_winner_index = None

st.title("🎡 カスタムルーレット")

# --- メインエリア ---
col_main, col_sidebar = st.columns([2, 1])

with col_main:
    # 外部 JS/CSS の安全な読み込み
    try:
        with open("src/assets/roulette/wheel.js", encoding="utf-8", errors="replace") as f:
            wheel_js = f.read()
        with open("src/assets/roulette/style.css", encoding="utf-8", errors="replace") as f:
            wheel_css = f.read()
    except Exception as e:
        wheel_js = f"console.error('Asset Load Error: {e}');"
        wheel_css = ""

    # ルーレット描画用のコンポーネント
    def render_roulette_canvas(items, sound_enabled, spin_trigger, winner_index):
        norm_items = normalize_weights(items)
        items_json = json.dumps(norm_items, ensure_ascii=True)
        html_template = """
        <style> __CSS__ </style>
        <div id="container">
            <canvas id="wheel" width="450" height="450"></canvas>
            <div id="status">__STATUS__</div>
        </div>
        <script>
            __JS__
            const config = {
                items: __ITEMS__,
                soundEnabled: __SOUND__,
                spinTrigger: __TRIGGER__,
                winnerIndex: __WINNER__
            };
            setupWheel(config);
        </script>
        <!-- refresh_key: __TRIGGER__ -->
        """
        full_html = (
            html_template.replace("__CSS__", str(wheel_css))
            .replace("__JS__", str(wheel_js))
            .replace("__STATUS__", "抽選中..." if spin_trigger > 0 else "")
            .replace("__ITEMS__", str(items_json))
            .replace("__SOUND__", "true" if sound_enabled else "false")
            .replace("__TRIGGER__", str(int(spin_trigger)))
            .replace("__WINNER__", json.dumps(winner_index))
        )
        st.components.v1.html(str(full_html), height=550)

    # 描画実行
    render_roulette_canvas(
        st.session_state.roulette_config["items"],
        st.session_state.roulette_config["sound_enabled"],
        st.session_state.roulette_spin_trigger,
        st.session_state.roulette_winner_index,
    )

    if st.button("🚀 ルーレットを回す！", use_container_width=True, type="primary"):
        # 1. Python で先に結果を出す
        items = st.session_state.roulette_config["items"]
        winner = pick_roulette_winner(items)

        winner_idx = 0
        for i, item in enumerate(items):
            if item["label"] == winner["label"]:
                winner_idx = i
                break

        # 2. セッション状態を更新
        st.session_state.roulette_last_winner = winner
        st.session_state.roulette_winner_index = winner_idx
        st.session_state.roulette_spin_trigger += 1

        # 3. 履歴追加
        history_entry = {
            "time": time.strftime("%H:%M:%S"),
            "label": str(winner["label"]),
            "color": str(winner["color"]),
        }
        st.session_state.roulette_history.insert(0, history_entry)
        st.session_state.roulette_history = st.session_state.roulette_history[:50]
        storage.set_item("roulette_history", st.session_state.roulette_history)

        st.rerun()

    # --- 演出エリア（ここ全体を遅延表示させる） ---
    if st.session_state.roulette_last_winner and st.session_state.roulette_spin_trigger > 0:
        # この div 内にあるものは 4.8 秒後に表示される
        st.markdown('<div class="reveal-area">', unsafe_allow_html=True)

        st.success(f"結果：{st.session_state.roulette_last_winner['label']}")
        st.balloons()

        # 履歴も同じタイミングで表示
        st.subheader("📜 履歴")
        if st.session_state.roulette_history:
            for entry in st.session_state.roulette_history[:10]:
                st.markdown(
                    f"- **{entry['time']}**: <span style='color:{entry['color']}'>●</span> {entry['label']}",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # 初回表示時やリセット時
        st.subheader("📜 履歴")
        if st.session_state.roulette_history:
            for entry in st.session_state.roulette_history[:10]:
                st.markdown(
                    f"- **{entry['time']}**: <span style='color:{entry['color']}'>●</span> {entry['label']}",
                    unsafe_allow_html=True,
                )
        else:
            st.info("履歴はまだありません。")

# --- サイドバー ---
with col_sidebar:
    st.subheader("⚙️ 設定")

    with st.expander("📝 項目と重みの編集", expanded=True):
        new_items = []
        for i, item in enumerate(st.session_state.roulette_config["items"]):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                label = st.text_input(f"名前 {i + 1}", value=item["label"], key=f"label_{i}")
            with c2:
                weight = st.number_input(
                    "重み", value=float(item.get("weight", 1.0)), min_value=0.0, step=0.1, key=f"weight_{i}"
                )
            with c3:
                color = st.color_picker("色", value=item.get("color", "#CCCCCC"), key=f"color_{i}")
                if st.button("🗑️", key=f"del_{i}"):
                    continue
            new_items.append({"label": label, "weight": weight, "color": color})

        if st.button("➕ 項目を追加"):
            rand_color = f"#{random.randint(0, 0xFFFFFF):06x}"
            new_items.append({"label": "新しい項目", "weight": 1.0, "color": rand_color})
            st.rerun()

        if st.button("💾 設定を保存"):
            st.session_state.roulette_config["items"] = new_items
            storage.set_item("roulette_config", st.session_state.roulette_config)
            st.success("保存しました！")
            st.rerun()

    st.session_state.roulette_config["sound_enabled"] = st.toggle(
        "🔊 カチカチ音を有効にする", value=st.session_state.roulette_config.get("sound_enabled", True)
    )

    st.write("---")
    st.subheader("📁 設定の共有")

    # JSON出力
    json_data = json.dumps(st.session_state.roulette_config, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 JSON保存",
        data=json_data,
        file_name="roulette_config.json",
        mime="application/json",
        use_container_width=True,
    )

    # JSON読込
    uploaded_file = st.file_uploader("📤 JSON読込", type="json")
    if uploaded_file is not None:
        if st.button("設定を反映", use_container_width=True):
            try:
                data = json.load(uploaded_file)
                is_valid, msg = validate_roulette_config(data)
                if is_valid:
                    migrated = migrate_roulette_config(data)
                    st.session_state.roulette_config = migrated
                    storage.set_item("roulette_config", migrated)
                    st.success("反映しました！")
                    st.rerun()
                else:
                    st.error(f"無効なデータ: {msg}")
            except Exception as e:
                st.error(f"読込失敗: {e}")

    if st.button("🗑️ 履歴をクリア", use_container_width=True):
        st.session_state.roulette_history = []
        storage.set_item("roulette_history", [])
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
