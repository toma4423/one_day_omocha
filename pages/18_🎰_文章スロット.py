import json
import time

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.sentence_slot import (
    SentenceSlotConfig,
    migrate_sentence_slot_data,
    pick_random_item,
)
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_storage_controls,
    wait_for_storage_load,
)

# ページ基本設定
st.set_page_config(page_title="文章スロット", page_icon="🎰", layout="wide")

# グローバルスタイルの適用
render_page_header()

storage = SafeStorage(LocalStorage())
DATA_KEY = "sentence_slot_data_v1"

# --- 初期化とデータ復元 ---
if "ss_config" not in st.session_state:
    saved_data = wait_for_storage_load(storage, DATA_KEY, "_ss_initialized")
    if saved_data:
        st.session_state.ss_config = migrate_sentence_slot_data(saved_data.get("config"))
    else:
        st.session_state.ss_config = SentenceSlotConfig()

    # 演出用の状態
    config = st.session_state.ss_config
    st.session_state.ss_targets = [reel.items[0] if reel.items else "" for reel in config.reels]
    st.session_state.ss_spinning = [False] * 3
    st.session_state.ss_trigger = 0
    st.session_state.last_saved_ss = st.session_state.ss_config.model_dump_json()
    st.rerun()
    st.stop()

if "ss_config" not in st.session_state:
    st.stop()

config: SentenceSlotConfig = st.session_state.ss_config
is_dirty = st.session_state.last_saved_ss != config.model_dump_json()

st.title("🎰 文章スロット")
st.caption("「誰が」「何を」「どうした」を組み合わせて面白い文章を作ろう！")

# --- 保存忘れ警告 ---
if is_dirty:
    st.warning("⚠️ 変更が保存されていません。下の「データの管理」から保存してください。")

# --- アセットの読み込み ---
try:
    with open("src/assets/sentence_slot/style.css", encoding="utf-8") as f:
        ss_css = f.read()
    with open("src/assets/sentence_slot/reel.js", encoding="utf-8") as f:
        ss_js = f.read()
except Exception as e:
    st.error(f"アセットの読み込みに失敗しました: {e}")
    ss_css = ""
    ss_js = ""


# --- スロット描画関数 ---
def render_sentence_slot(config: SentenceSlotConfig, targets: list[str], spinning: list[bool], trigger: int):
    reels_data = []
    # 状態の一貫性を保つため、現在の config の内容をシリアライズ
    config_json = config.model_dump_json()

    for i, reel in enumerate(config.reels):
        display_items = reel.items if reel.items else ["(空)"]
        reels_data.append({"items": display_items, "target": targets[i], "isSpinning": spinning[i]})

    html_template = f"""
    <style>{ss_css}</style>
    <div id="sentence-slot-app">
        <div class="sentence-slot-container">
            {''.join([f'''
            <div class="reel-wrapper" id="reel-wrapper-{i}">
                <div class="reel-content">
                    {''.join([f'<div class="reel-item">{item}</div>' for item in (reel.items if reel.items else ["(空)"]) * 10])}
                </div>
            </div>
            ''' for i, reel in enumerate(config.reels)])}
        </div>
    </div>
    <script>
        {ss_js}
        setupSentenceSlot({{
            reels: {json.dumps(reels_data, ensure_ascii=False)},
            trigger: {trigger}
        }});
    </script>
    """
    # keyに config_json と trigger を含めることで、項目が編集された際や回転時に確実に再読み込みさせる
    st.components.v1.html(html_template, height=200, key=f"ss_html_{hash(config_json)}_{trigger}")


# --- スロット操作 ---
c_all, _ = st.columns([1, 2])
with c_all:
    if st.button("🔥 全てまとめて回転！", use_container_width=True, type="primary"):
        for i in range(len(config.reels)):
            if config.reels[i].items:
                st.session_state.ss_targets[i] = pick_random_item(config.reels[i].items)
                st.session_state.ss_spinning[i] = True
        st.session_state.ss_trigger += 1
        st.rerun()

render_sentence_slot(config, st.session_state.ss_targets, st.session_state.ss_spinning, st.session_state.ss_trigger)

# 各リールの個別ボタン
cols = st.columns(3)
for i, reel in enumerate(config.reels):
    with cols[i]:
        if st.button(f"🔄 {reel.name}を回す", key=f"spin_{i}", use_container_width=True):
            if reel.items:
                st.session_state.ss_targets[i] = pick_random_item(reel.items)
                st.session_state.ss_spinning = [False] * 3  # 他を止める
                st.session_state.ss_spinning[i] = True
                st.session_state.ss_trigger += 1
                st.rerun()

# 演出終了フラグを落とす（リロード時）
if any(st.session_state.ss_spinning):
    time.sleep(0.1)  # 演出時間を考慮
    st.session_state.ss_spinning = [False] * 3

st.write("---")

# --- 編集エリア ---
st.subheader("📝 項目を編集する")
edit_cols = st.columns(3)

for i, reel in enumerate(config.reels):
    with edit_cols[i]:
        st.markdown(f"### {reel.name}")

        # 追加用
        new_item = st.text_input(
            f"新しい項目を追加 ({reel.name})",
            key=f"add_input_{i}",
            label_visibility="collapsed",
            placeholder=f"{reel.name}...",
        )
        if st.button("➕ 追加", key=f"add_btn_{i}", use_container_width=True):
            if new_item and new_item not in reel.items:
                reel.items.append(new_item)
                st.rerun()

        # 既存項目リスト
        st.write("")
        for idx, item in enumerate(reel.items):
            ic1, ic2 = st.columns([4, 1])
            ic1.write(f"・{item}")
            if ic2.button("❌", key=f"del_{i}_{idx}"):
                reel.items.pop(idx)
                st.rerun()

st.write("---")


# --- データの管理 ---
def on_load(data: dict):
    st.session_state.ss_config = migrate_sentence_slot_data(data.get("config"))
    st.session_state.last_saved_ss = st.session_state.ss_config.model_dump_json()


def on_save():
    st.session_state.last_saved_ss = config.model_dump_json()


render_storage_controls(
    storage=storage,
    storage_key=DATA_KEY,
    current_data={"config": config.model_dump()},
    on_load_callback=on_load,
    on_save_callback=on_save,
    file_prefix="sentence_slot",
)

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
