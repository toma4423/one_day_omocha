import json
import random
import time

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.roulette import (
    equalize_weights,
    migrate_roulette_config,
    normalize_weights,
    pick_roulette_winner,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header

# ページ基本設定
st.set_page_config(page_title="ルーレット", page_icon="🎡", layout="wide")

# グローバルスタイルの適用
render_page_header()

# 強力な遅延表示用 CSS
st.markdown(
    """
<style>
@keyframes waitThenShow {
    0% { opacity: 0; max-height: 0; overflow: hidden; pointer-events: none; margin: 0; }
    98% { opacity: 0; max-height: 0; overflow: hidden; pointer-events: none; margin: 0; }
    100% { opacity: 1; max-height: 2000px; overflow: visible; pointer-events: auto; }
}
.strictly-delayed {
    animation: waitThenShow 5.0s forwards;
}
</style>
""",
    unsafe_allow_html=True,
)

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# 設定のロード
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
    # 外部 JS/CSS の読み込み
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
        items = st.session_state.roulette_config["items"]
        winner = pick_roulette_winner(items)

        winner_idx = 0
        for i, item in enumerate(items):
            if item["label"] == winner["label"]:
                winner_idx = i
                break

        st.session_state.roulette_last_winner = winner
        st.session_state.roulette_winner_index = winner_idx
        st.session_state.roulette_spin_trigger += 1

        history_entry = {
            "time": time.strftime("%H:%M:%S"),
            "label": str(winner["label"]),
            "color": str(winner["color"]),
        }
        st.session_state.roulette_history.insert(0, history_entry)
        st.session_state.roulette_history = st.session_state.roulette_history[:50]
        storage.set_item("roulette_history", st.session_state.roulette_history)

        st.rerun()

    # --- データの保存と読み込み ---
    st.write("")
    with st.container(border=True):
        st.subheader("📁 データの保存と読み込み")
        c1, c2 = st.columns(2)
        with c1:
            json_data = json.dumps(st.session_state.roulette_config, ensure_ascii=False, indent=2)
            st.download_button(
                "📥 設定をJSONで保存", json_data, "roulette_config.json", "application/json", use_container_width=True
            )
        with c2:
            uploaded_file = st.file_uploader("📤 設定JSONを読み込む", type="json", label_visibility="collapsed")
            if uploaded_file and st.button("反映実行", use_container_width=True):
                try:
                    data = json.load(uploaded_file)
                    migrated = migrate_roulette_config(data)
                    st.session_state.roulette_config = migrated
                    storage.set_item("roulette_config", migrated)
                    st.success("反映しました！")
                    st.rerun()
                except Exception as e:
                    st.error(f"読込失敗: {e}")

    # --- 履歴セクション ---
    container_class = "strictly-delayed" if st.session_state.roulette_spin_trigger > 0 else ""
    with st.container():
        st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
        with st.expander("📜 抽選履歴を表示する"):
            if st.session_state.roulette_history:
                for entry in st.session_state.roulette_history[:15]:
                    st.markdown(
                        f"- **{entry['time']}**: <span style='color:{entry['color']}'>●</span> {entry['label']}",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("履歴はまだありません。")
        st.markdown("</div>", unsafe_allow_html=True)

# --- サイドバー ---
with col_sidebar:
    st.subheader("⚙️ 設定")

    with st.expander("📝 項目と重みの編集", expanded=True):
        items = st.session_state.roulette_config["items"]
        new_items = []
        to_delete = None

        for i, item in enumerate(items):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                label = st.text_input(f"名前 {i + 1}", value=item["label"], key=f"label_{i}")
            with c2:
                weight = st.number_input(
                    f"重み {i + 1}",
                    value=float(item.get("weight", 1.0)),
                    min_value=0.0,
                    step=0.1,
                    key=f"weight_{i}",
                    label_visibility="collapsed",
                )
            with c3:
                st.color_picker(
                    "色", value=item.get("color", "#CCCCCC"), key=f"color_{i}", label_visibility="collapsed"
                )
                if st.button("🗑️", key=f"del_{i}"):
                    to_delete = i

            # 削除対象でない場合のみリストに追加
            new_items.append({"label": label, "weight": weight, "color": st.session_state[f"color_{i}"]})

        # 削除処理の実行
        if to_delete is not None:
            new_items.pop(to_delete)
            st.session_state.roulette_config["items"] = new_items
            storage.set_item("roulette_config", st.session_state.roulette_config)
            st.rerun()

        st.write("---")
        col_add, col_auto = st.columns(2)
        with col_add:
            if st.button("➕ 追加", use_container_width=True):
                rand_color = f"#{random.randint(0, 0xFFFFFF):06x}"
                new_items.append({"label": "新しい項目", "weight": 1.0, "color": rand_color})
                st.session_state.roulette_config["items"] = new_items
                storage.set_item("roulette_config", st.session_state.roulette_config)
                st.rerun()

        with col_auto:
            if st.button("⚖️ 均等化", use_container_width=True, help="すべての重みを均等にします"):
                st.session_state.roulette_config["items"] = equalize_weights(new_items)
                storage.set_item("roulette_config", st.session_state.roulette_config)
                st.success("重みを均等にしました")
                st.rerun()

        if st.button("💾 設定を保存", use_container_width=True, type="primary"):
            st.session_state.roulette_config["items"] = normalize_weights(new_items)
            storage.set_item("roulette_config", st.session_state.roulette_config)
            st.success("保存しました！")
            st.rerun()

    st.session_state.roulette_config["sound_enabled"] = st.toggle(
        "🔊 カチカチ音を有効にする", value=st.session_state.roulette_config.get("sound_enabled", True)
    )

    if st.button("🗑️ 履歴をクリア", use_container_width=True):
        st.session_state.roulette_history = []
        storage.set_item("roulette_history", [])
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
