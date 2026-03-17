import random
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
DATA_KEY = "sentence_slot_data_v2"  # キーを更新してクリーンにする

# --- 初期化とデータ復元 ---
if "ss_config" not in st.session_state:
    saved_data = wait_for_storage_load(storage, DATA_KEY, "_ss_initialized")
    if saved_data:
        st.session_state.ss_config = migrate_sentence_slot_data(saved_data.get("config"))
    else:
        st.session_state.ss_config = SentenceSlotConfig()

    config_init = st.session_state.ss_config
    st.session_state.ss_results = [reel.items[0] if reel.items else "---" for reel in config_init.reels]
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

# --- スロット表示エリア ---
# カスタムCSSで見た目を整える
st.markdown(
    """
<style>
.slot-container {
    display: flex;
    justify-content: center;
    gap: 15px;
    padding: 25px;
    background: #f8f9fa;
    border-radius: 20px;
    border: 2px solid #dee2e6;
    margin-bottom: 20px;
}
.slot-box {
    flex: 1;
    background: white;
    border: 3px solid #333;
    border-radius: 12px;
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 900;
    color: #000;
    padding: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
@media (max-width: 768px) {
    .slot-container { flex-direction: column; }
    .slot-box { height: 80px; font-size: 1.2rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

# プレースホルダー作成
placeholders = st.columns(3)
slot_boxes = [p.empty() for p in placeholders]


def update_display():
    for i, box in enumerate(slot_boxes):
        text = st.session_state.ss_results[i]
        box.markdown(f"<div class='slot-box'>{text}</div>", unsafe_allow_html=True)


update_display()


# --- スロット操作 ---
def spin_reel(reel_idx: int):
    reel = config.reels[reel_idx]
    if not reel.items:
        return

    # シャッフル演出（Python側で制御）
    steps = 10
    for _s in range(steps):
        temp_text = random.choice(reel.items)
        slot_boxes[reel_idx].markdown(
            f"<div class='slot-box' style='opacity: 0.5;'>{temp_text}</div>", unsafe_allow_html=True
        )
        time.sleep(0.05)

    # 最終結果
    final_text = pick_random_item(reel.items)
    st.session_state.ss_results[reel_idx] = final_text
    update_display()


# 個別ボタン
btn_cols = st.columns(3)
for i, reel in enumerate(config.reels):
    if btn_cols[i].button(f"🔄 {reel.name}", key=f"spin_btn_{i}", use_container_width=True):
        spin_reel(i)
        st.rerun()

# 全てまとめて回転ボタン（下部に全幅で配置）
if st.button("🔥 全てまとめて回転！", use_container_width=True, type="primary"):
    # 全て並列風に見せるために演出を工夫
    for _s in range(10):
        for i, reel in enumerate(config.reels):
            if reel.items:
                temp = random.choice(reel.items)
                slot_boxes[i].markdown(
                    f"<div class='slot-box' style='opacity: 0.5;'>{temp}</div>", unsafe_allow_html=True
                )
        time.sleep(0.05)

    for i, reel in enumerate(config.reels):
        if reel.items:
            st.session_state.ss_results[i] = pick_random_item(reel.items)
    st.rerun()

st.write("---")

# --- 編集エリア ---
st.subheader("📝 項目を編集する")
edit_cols = st.columns(3)

for i, reel in enumerate(config.reels):
    with edit_cols[i]:
        st.markdown(f"### {reel.name}")

        new_item = st.text_input(
            f"追加 ({reel.name})", key=f"add_in_{i}", label_visibility="collapsed", placeholder=f"{reel.name}を入力..."
        )
        if st.button("➕ 追加", key=f"add_bt_{i}", use_container_width=True):
            if new_item and new_item not in reel.items:
                reel.items.append(new_item)
                st.rerun()

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
