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
from src.utils.styles import render_donation_box

st.set_page_config(page_title="ルーレット", page_icon="🎡", layout="wide")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# 設定のロード
if "roulette_config" not in st.session_state:
    saved_config = storage.get_item("roulette_config", is_json=True)
    st.session_state.roulette_config = migrate_roulette_config(saved_config)

# 抽選履歴の初期化
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
    # 外部 JS/CSS を読み込む
    try:
        with open("src/assets/roulette/wheel.js", encoding="utf-8") as f:
            wheel_js = f.read()
        with open("src/assets/roulette/style.css", encoding="utf-8") as f:
            wheel_css = f.read()
    except Exception:
        wheel_js = ""
        wheel_css = ""

    # ルーレット描画用のコンポーネント
    def render_roulette_canvas(items, sound_enabled, spin_trigger, winner_index):
        # 描画前に重みを正規化する
        normalized_items = normalize_weights(items)
        items_json = json.dumps(normalized_items, ensure_ascii=False)
        sound_enabled_js = "true" if sound_enabled else "false"
        status_text = "抽選中..." if spin_trigger > 0 else ""

        # f-string の中でのブレース問題を避けるため、CSSとJSは分割して結合する
        html_head = "<style>" + wheel_css + "</style>"
        html_body = f"""
        <div id="container">
            <canvas id="wheel" width="450" height="450"></canvas>
            <div id="status">{status_text}</div>
        </div>
        """
        html_script = f"""
        <script>
            {wheel_js}
            const config = {{
                items: {items_json},
                soundEnabled: {sound_enabled_js},
                spinTrigger: {spin_trigger},
                winnerIndex: {json.dumps(winner_index)}
            }};
            setupWheel(config);
        </script>
        """

        full_html = html_head + html_body + html_script

        # key を指定することで、毎回 iframe が作り直され、アニメーションが確実に最初から走る
        st.components.v1.html(full_html, height=550, key=f"roulette_comp_{spin_trigger}")

    # 描画 (trigger が 0 より大きければアニメーション開始)
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

        # IDや一意の識別子がないため、名前で一致を確認
        # 本来はID管理が望ましいが、現状のデータ構造に合わせる
        winner_idx = 0
        for i, item in enumerate(items):
            if item["label"] == winner["label"]:
                winner_idx = i
                break

        # 2. セッション状態を更新 (Trigger を変えることで JS が動く)
        st.session_state.roulette_last_winner = winner
        st.session_state.roulette_winner_index = winner_idx
        st.session_state.roulette_spin_trigger += 1  # 毎回違う値にする

        # 3. 履歴追加
        history_entry = {"time": time.strftime("%H:%M:%S"), "label": winner["label"], "color": winner["color"]}
        st.session_state.roulette_history.insert(0, history_entry)
        st.session_state.roulette_history = st.session_state.roulette_history[:50]
        storage.set_item("roulette_history", st.session_state.roulette_history)

        st.rerun()

    if st.session_state.roulette_last_winner and st.session_state.roulette_spin_trigger > 0:
        # アニメーションが終わるまで少し待つ演出
        time.sleep(0.5)
        st.success(f"結果：{st.session_state.roulette_last_winner['label']}")
        st.balloons()

    # 履歴表示
    st.subheader("📜 履歴")
    if st.session_state.roulette_history:
        for entry in st.session_state.roulette_history[:10]:
            st.markdown(
                f"- **{entry['time']}**: <span style='color:{entry['color']}'>●</span> {entry['label']}",
                unsafe_allow_html=True,
            )
    else:
        st.info("履歴はまだありません。")

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
                    "重み", value=float(item["weight"]), min_value=0.0, step=0.1, key=f"weight_{i}"
                )
            with c3:
                color = st.color_picker("色", value=item["color"], key=f"color_{i}")
                if st.button("🗑️", key=f"del_{i}"):
                    # 削除処理（リストから除外）
                    continue
            new_items.append({"label": label, "weight": weight, "color": color})

        if st.button("➕ 項目を追加"):
            # デフォルト色をランダムに
            rand_color = f"#{random.randint(0, 0xFFFFFF):06x}"
            new_items.append({"label": "新しい項目", "weight": 1.0, "color": rand_color})
            st.rerun()

        if st.button("💾 設定を保存"):
            st.session_state.roulette_config["items"] = new_items
            storage.set_item("roulette_config", st.session_state.roulette_config)
            st.success("保存しました！")
            st.rerun()

    st.session_state.roulette_config["sound_enabled"] = st.toggle(
        "🔊 カチカチ音を有効にする", value=st.session_state.roulette_config["sound_enabled"]
    )

    st.write("---")

    # ファイル入出力
    st.subheader("📁 設定の共有")

    # エクスポート
    json_data = json.dumps(st.session_state.roulette_config, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 設定をJSONで保存",
        data=json_data,
        file_name="roulette_config.json",
        mime="application/json",
    )

    # インポート
    uploaded_file = st.file_uploader("📤 設定JSONを読み込む", type="json")
    if uploaded_file is not None:
        if st.button("設定を反映", use_container_width=True):
            try:
                data = json.load(uploaded_file)
                is_valid, msg = validate_roulette_config(data)
                if is_valid:
                    migrated = migrate_roulette_config(data)
                    st.session_state.roulette_config = migrated
                    storage.set_item("roulette_config", migrated)
                    st.success("設定を反映しました！")
                    st.rerun()
                else:
                    st.error(f"エラー: {msg}")
            except Exception as e:
                st.error(f"JSONの読み込みに失敗しました: {e}")

    if st.button("🗑️ 履歴をクリア", use_container_width=True):
        st.session_state.roulette_history = []
        storage.set_item("roulette_history", [])
        st.rerun()

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
