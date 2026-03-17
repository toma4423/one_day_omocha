import json
import random
import time

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.roulette import (
    COLOR_PRESETS,
    RouletteConfig,
    RouletteItem,
    apply_color_preset,
    migrate_roulette_config,
    pick_roulette_winner,
)
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_storage_controls,
    wait_for_storage_load,
)
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

storage = SafeStorage(LocalStorage())
DATA_KEY = "roulette_data_v5"

# 設定のロード (堅牢な初期化)
if "roulette_config" not in st.session_state:
    saved_data = wait_for_storage_load(storage, DATA_KEY, "_roulette_initialized")

    # データの復元
    if saved_data:
        try:
            st.session_state.roulette_config = migrate_roulette_config(saved_data.get("config"))
            st.session_state.roulette_history = saved_data.get("history", [])
        except Exception:
            st.session_state.roulette_config = migrate_roulette_config(None)
            st.session_state.roulette_history = []
    else:
        st.session_state.roulette_config = migrate_roulette_config(None)
        st.session_state.roulette_history = []

    st.session_state.roulette_last_winner = None
    st.session_state.roulette_spin_trigger = 0
    st.session_state.roulette_winner_index = None

    # 変更検知用のスナップショット
    st.session_state.last_saved_config = st.session_state.roulette_config.model_dump_json()

    st.rerun()
    st.stop()

# 二重の安全策: 初期化が完了していない場合はここで停止
if "roulette_config" not in st.session_state:
    st.stop()

st.title("🎡 カスタムルーレット")

# --- 保存状態のチェック ---
config: RouletteConfig = st.session_state.roulette_config
is_dirty = st.session_state.last_saved_config != config.model_dump_json()

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
    def render_roulette_canvas(items: list[RouletteItem], sound_enabled, spin_trigger, winner_index):
        active_items = [it.model_dump() for it in items if it.enabled]
        items_json = json.dumps(active_items, ensure_ascii=True)
        html_template = """
        <style> __CSS__ </style>
        <div id="container">
            <canvas id="wheel" width="600" height="600"></canvas>
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
        st.components.v1.html(str(full_html), height=650)

    render_roulette_canvas(
        config.items,
        config.sound_enabled,
        st.session_state.roulette_spin_trigger,
        st.session_state.roulette_winner_index,
    )

    if st.button("🚀 ルーレットを回す！", use_container_width=True, type="primary"):
        active_items = [it for it in config.items if it.enabled]
        if not active_items:
            st.error("有効な項目がありません。")
        else:
            winner = pick_roulette_winner(config.items)
            winner_idx = 0
            for i, item in enumerate(active_items):
                if item.id == winner.id:
                    winner_idx = i
                    break
            st.session_state.roulette_last_winner = winner
            st.session_state.roulette_winner_index = winner_idx
            st.session_state.roulette_spin_trigger += 1
            history_entry = {
                "time": get_jst_now().strftime("%H:%M:%S"),
                "label": str(winner.label),
                "color": str(winner.color),
            }
            st.session_state.roulette_history.insert(0, history_entry)
            st.session_state.roulette_history = st.session_state.roulette_history[:50]
            st.rerun()

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
                if st.button("🗑️ 履歴をクリア", use_container_width=True):
                    st.session_state.roulette_history = []
                    st.rerun()
            else:
                st.info("履歴はまだありません。")
        st.markdown("</div>", unsafe_allow_html=True)

# --- サイドバー：設定 ---
with col_sidebar:
    st.subheader("⚙️ 設定")

    if is_dirty:
        st.warning("⚠️ 設定に変更があります。「ブラウザに保存」ボタンを押してください。")

    with st.expander("📝 項目と重みの編集", expanded=True):
        if st.button("➕ 項目を追加", use_container_width=True):
            new_id = f"item_{int(time.time() * 1000)}"
            rand_color = f"#{random.randint(0, 0xFFFFFF):06x}"
            config.items.append(
                RouletteItem(
                    id=new_id,
                    label=f"項目 {len(config.items) + 1}",
                    weight=0,
                    color=rand_color,
                    enabled=True,
                )
            )
            st.rerun()

        active_indices = [i for i, it in enumerate(config.items) if it.enabled]
        total_weight = sum(config.items[i].weight for i in active_indices)

        if total_weight != 100:
            diff = 100 - total_weight
            if st.button(f"⚖️ 残り{diff}%を自動配分", use_container_width=True):
                if active_indices:
                    n = len(active_indices)
                    base_change = diff // n
                    remainder = diff % n
                    for count, idx in enumerate(active_indices):
                        adj = base_change + (1 if count < remainder else 0)
                        config.items[idx].weight = int(max(0, config.items[idx].weight + adj))
                    new_total = sum(config.items[i].weight for i in active_indices)
                    if new_total != 100 and active_indices:
                        config.items[active_indices[0].weight] += 100 - new_total
                    st.rerun()

        preset_options = ["(カラーテーマを選択)"] + list(COLOR_PRESETS.keys())
        selected_preset = st.selectbox("🎨 配色プリセット", preset_options)
        if selected_preset != "(カラーテーマを選択)":
            config.items = apply_color_preset(config.items, selected_preset)
            st.rerun()

        st.write("---")

        new_items_list = []
        to_delete_id = None
        move_up_idx = -1
        move_down_idx = -1
        any_change = False

        for idx, item in enumerate(config.items):
            iid = item.id
            with st.container():
                c1, c2, c3 = st.columns([0.5, 3.5, 1.5])
                with c1:
                    new_enabled = st.checkbox("E", value=item.enabled, key=f"en_{iid}", label_visibility="collapsed")
                with c2:
                    new_label = st.text_input("L", value=item.label, key=f"lb_{iid}", label_visibility="collapsed")
                with c3:
                    new_weight = st.number_input(
                        "W",
                        value=int(item.weight),
                        min_value=0,
                        max_value=100,
                        key=f"wt_{iid}",
                        label_visibility="collapsed",
                    )

                c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
                with c1:
                    new_color = st.color_picker("C", value=item.color, key=f"cl_{iid}", label_visibility="collapsed")
                with c2:
                    if st.button("↑", key=f"up_{iid}", use_container_width=True, disabled=(idx == 0)):
                        move_up_idx = idx
                with c3:
                    if st.button(
                        "↓", key=f"dn_{iid}", use_container_width=True, disabled=(idx == len(config.items) - 1)
                    ):
                        move_down_idx = idx
                with c4:
                    if st.button("🗑️", key=f"dl_{iid}", use_container_width=True):
                        to_delete_id = iid

                updated_item = RouletteItem(
                    id=iid,
                    label=new_label,
                    weight=new_weight,
                    color=new_color,
                    enabled=new_enabled,
                )
                new_items_list.append(updated_item)
                if updated_item != item:
                    any_change = True
                st.markdown("<hr style='margin: 5px 0 !important;'>", unsafe_allow_html=True)

        if to_delete_id:
            config.items = [it for it in new_items_list if it.id != to_delete_id]
            st.rerun()
        elif move_up_idx > 0:
            new_items_list[move_up_idx], new_items_list[move_up_idx - 1] = (
                new_items_list[move_up_idx - 1],
                new_items_list[move_up_idx],
            )
            config.items = new_items_list
            st.rerun()
        elif move_down_idx >= 0 and move_down_idx < len(new_items_list) - 1:
            new_items_list[move_down_idx], new_items_list[move_down_idx + 1] = (
                new_items_list[move_down_idx + 1],
                new_items_list[move_down_idx],
            )
            config.items = new_items_list
            st.rerun()
        elif any_change:
            config.items = new_items_list
            st.rerun()

    config.sound_enabled = st.toggle("🔊 効果音を有効にする", value=config.sound_enabled)

    def on_load_roulette(data: dict):
        st.session_state.roulette_config = migrate_roulette_config(data.get("config", data))
        if "history" in data:
            st.session_state.roulette_history = data["history"]
        st.session_state.last_saved_config = st.session_state.roulette_config.model_dump_json()

    def on_save_roulette():
        st.session_state.last_saved_config = st.session_state.roulette_config.model_dump_json()

    render_storage_controls(
        storage=storage,
        storage_key=DATA_KEY,
        current_data={"config": config.model_dump(), "history": st.session_state.roulette_history},
        on_load_callback=on_load_roulette,
        on_save_callback=on_save_roulette,
        file_prefix="roulette_data",
    )

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
