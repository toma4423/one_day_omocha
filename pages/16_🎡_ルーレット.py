import json
import random
import time

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.roulette import (
    COLOR_PRESETS,
    apply_color_preset,
    migrate_roulette_config,
    pick_roulette_winner,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header
from src.utils.time import get_jst_now

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
hr { margin: 15px 0 !important; border: 0; border-top: 2px solid #f0f2f6; }
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
        # 有効な項目のみを抽出して渡す
        active_items = [it for it in items if it.get("enabled", True)]
        items_json = json.dumps(active_items, ensure_ascii=True)
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
        # 有効な項目のみから抽選
        active_items = [it for it in items if it.get("enabled", True)]
        if not active_items:
            st.error("有効な項目がありません。")
        else:
            winner = pick_roulette_winner(items)
            # 全項目の中でのインデックスではなく、有効な項目の中でのインデックスを渡す
            winner_idx = 0
            for i, item in enumerate(active_items):
                if item["id"] == winner["id"]:
                    winner_idx = i
                    break

            st.session_state.roulette_last_winner = winner
            st.session_state.roulette_winner_index = winner_idx
            st.session_state.roulette_spin_trigger += 1
            history_entry = {
                "time": get_jst_now().strftime("%H:%M:%S"),
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

# --- サイドバー：設定 ---
with col_sidebar:
    st.subheader("⚙️ 設定")

    with st.expander("📝 項目と重みの編集", expanded=True):
        # 編集中のリストをセッションから取得
        current_items = st.session_state.roulette_config["items"]

        # 1. 操作系ボタン（追加、合計確認）
        if st.button("➕ 項目を追加", use_container_width=True):
            new_id = f"item_{int(time.time() * 1000)}"
            rand_color = f"#{random.randint(0, 0xFFFFFF):06x}"
            current_items.append(
                {
                    "id": new_id,
                    "label": f"項目 {len(current_items) + 1}",
                    "weight": 0,
                    "color": rand_color,
                    "enabled": True,
                }
            )
            st.session_state.roulette_config["items"] = current_items
            storage.set_item("roulette_config", st.session_state.roulette_config)
            st.rerun()

        # 現在の合計を計算
        active_indices = [i for i, it in enumerate(current_items) if it.get("enabled", True)]
        total_weight = sum(current_items[i]["weight"] for i in active_indices)

        if total_weight != 100:
            diff = 100 - total_weight
            st.warning(f"⚠️ 合計が {total_weight}% です（あと {diff}% 必要です）")

            if st.button("⚖️ 残りを自動配分", use_container_width=True):
                if active_indices:
                    n = len(active_indices)
                    base_change = diff // n
                    remainder = diff % n

                    new_items = [it.copy() for it in current_items]
                    for count, idx in enumerate(active_indices):
                        adj = base_change + (1 if count < remainder else 0)
                        new_val = max(0, new_items[idx]["weight"] + adj)
                        new_items[idx]["weight"] = int(new_val)

                    new_total = sum(new_items[i]["weight"] for i in active_indices)
                    if new_total != 100 and active_indices:
                        new_items[active_indices[0]]["weight"] += 100 - new_total

                    st.session_state.roulette_config["items"] = new_items
                    storage.set_item("roulette_config", st.session_state.roulette_config)
                    st.rerun()
                else:
                    st.error("有効な項目がありません。")

        # 2. カラープリセット
        preset_options = ["(カラーテーマを適用)"] + list(COLOR_PRESETS.keys())
        selected_preset = st.selectbox("🎨 プリセット", preset_options, label_visibility="collapsed")
        if selected_preset != "(カラーテーマを適用)":
            st.session_state.roulette_config["items"] = apply_color_preset(current_items, selected_preset)
            storage.set_item("roulette_config", st.session_state.roulette_config)
            st.rerun()

        st.write("---")

        # 3. 項目ループ
        new_items_list = []
        to_delete_id = None
        move_up_idx = -1
        move_down_idx = -1
        any_change = False

        for idx, item in enumerate(current_items):
            iid = item["id"]
            with st.container():
                # 上段：ラベルと有効化
                col_en, col_lab, col_weight = st.columns([0.5, 3.5, 1])
                with col_en:
                    new_enabled = st.checkbox(
                        "有効", value=item.get("enabled", True), key=f"enabled_{iid}", label_visibility="collapsed"
                    )
                with col_lab:
                    new_label = st.text_input(
                        "名前", value=item["label"], key=f"label_{iid}", label_visibility="collapsed"
                    )
                with col_weight:
                    new_weight = st.number_input(
                        "重み",
                        value=int(item["weight"]),
                        min_value=0,
                        max_value=100,
                        step=1,
                        format="%d",
                        key=f"weight_{iid}",
                        label_visibility="collapsed",
                    )

                # 下段：色、並び替え、削除
                col_col, col_up, col_down, col_del = st.columns([2, 1, 1, 1])
                with col_col:
                    new_color = st.color_picker(
                        "色", value=item["color"], key=f"color_{iid}", label_visibility="collapsed"
                    )
                with col_up:
                    if st.button("↑", key=f"up_{iid}", use_container_width=True, disabled=(idx == 0)):
                        move_up_idx = idx
                with col_down:
                    if st.button(
                        "↓", key=f"down_{iid}", use_container_width=True, disabled=(idx == len(current_items) - 1)
                    ):
                        move_down_idx = idx
                with col_del:
                    if st.button("🗑️", key=f"del_{iid}", use_container_width=True):
                        to_delete_id = iid

                # 変更検知
                updated_item = {
                    "id": iid,
                    "label": new_label,
                    "weight": new_weight,
                    "color": new_color,
                    "enabled": new_enabled,
                }
                new_items_list.append(updated_item)

                if updated_item != item:
                    any_change = True

                st.markdown("<hr style='margin: 5px 0 !important;'>", unsafe_allow_html=True)

        # 変更・並び替え・削除処理
        rerun_needed = False
        if to_delete_id:
            new_items_list = [it for it in new_items_list if it["id"] != to_delete_id]
            rerun_needed = True
        elif move_up_idx > 0:
            new_items_list[move_up_idx], new_items_list[move_up_idx - 1] = (
                new_items_list[move_up_idx - 1],
                new_items_list[move_up_idx],
            )
            rerun_needed = True
        elif move_down_idx >= 0 and move_down_idx < len(new_items_list) - 1:
            new_items_list[move_down_idx], new_items_list[move_down_idx + 1] = (
                new_items_list[move_down_idx + 1],
                new_items_list[move_down_idx],
            )
            rerun_needed = True
        elif any_change:
            rerun_needed = True

        if rerun_needed:
            st.session_state.roulette_config["items"] = new_items_list
            storage.set_item("roulette_config", st.session_state.roulette_config)
            st.rerun()

        if st.button("💾 設定を確定して保存", use_container_width=True, type="primary"):
            st.session_state.roulette_config["items"] = new_items_list
            storage.set_item("roulette_config", st.session_state.roulette_config)
            st.success("設定を保存しました！")
            st.rerun()

    st.session_state.roulette_config["sound_enabled"] = st.toggle(
        "🔊 カチカチ音を有効にする", value=st.session_state.roulette_config.get("sound_enabled", True)
    )

    if st.button("🗑️ 履歴をクリア", use_container_width=True):
        st.session_state.roulette_history = []
        storage.set_item("roulette_history", [])
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
