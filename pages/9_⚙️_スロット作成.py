import json

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.slot import DEFAULT_PAYOUTS, DEFAULT_SYMBOLS, get_slot_config
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box
from src.utils.time import get_jst_now

st.set_page_config(page_title="スロット作成", page_icon="⚙️", layout="wide")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# 設定のロード
if "slot_config_edit" not in st.session_state:
    saved_config = storage.get_item("slot_config", is_json=True)
    st.session_state.slot_config_edit = get_slot_config(saved_config)

st.title("⚙️ スロットカスタマイズ")

# --- サイドバー：セーブ＆ロード ---
with st.sidebar:
    st.header("💾 セーブ & ロード")

    # JSONセーブ
    json_str = json.dumps(st.session_state.slot_config_edit, indent=2, ensure_ascii=False)
    timestamp = get_jst_now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="設定をJSONで保存",
        data=json_str,
        file_name=f"slot_config_{timestamp}.json",
        mime="application/json",
        use_container_width=True,
    )

    # JSONロード
    uploaded_file = st.file_uploader("設定JSONを読込", type="json")
    if uploaded_file is not None:
        if st.button("設定を復元する", use_container_width=True):
            try:
                data_load = json.load(uploaded_file)
                # 簡易的なバリデーション
                if "symbols" in data_load and "payouts" in data_load:
                    st.session_state.slot_config_edit = data_load
                    storage.set_item("slot_config", data_load)
                    if "slot_config" in st.session_state:
                        st.session_state.slot_config = data_load
                    st.success("設定を復元しました！")
                    st.rerun()
                else:
                    st.error("不正な設定ファイル形式です")
            except Exception:
                st.error("JSONの読み込みに失敗しました")
    st.write("---")

st.info("スロットの図柄や役（パターンと配当）を自由にカスタマイズできます。変更は自動的にブラウザに保存されます。")

# --- 図柄の編集 ---
st.subheader("🖼️ 図柄（シンボル）の編集")
st.write("各リールに出現する図柄をカンマ区切りで入力してください。")

symbols_str = st.text_input(
    "図柄のリスト", ", ".join(st.session_state.slot_config_edit["symbols"]), key="symbols_edit_input"
)

# --- 役の編集 ---
st.write("---")
st.subheader("💰 役と配当の設定")
st.write(
    "各役の名称、図柄パターン、スコアを設定します。パターンのどこかに `ANY` を入れると、そのマスは何の図柄でも成立します。"
)

# 役の一覧を表示し、削除や編集を行う
new_payouts = []
for i, payout in enumerate(st.session_state.slot_config_edit["payouts"]):
    with st.expander(f"役 {i + 1}: {payout['name']}"):
        col_name, col_score = st.columns([3, 1])
        with col_name:
            p_name = st.text_input("役名", payout["name"], key=f"p_name_{i}")
        with col_score:
            p_score = st.number_input("スコア", value=payout["score"], min_value=0, step=1, key=f"p_score_{i}")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            p_1 = st.text_input("左リール", payout["pattern"][0], key=f"p_1_{i}")
        with col_p2:
            p_2 = st.text_input("中リール", payout["pattern"][1], key=f"p_2_{i}")
        with col_p3:
            p_3 = st.text_input("右リール", payout["pattern"][2], key=f"p_3_{i}")

        is_delete = st.checkbox("この役を削除する", key=f"del_{i}")
        if not is_delete:
            new_payouts.append({"name": p_name, "score": p_score, "pattern": [p_1, p_2, p_3]})

# 新しい役を追加
st.write("---")
st.write("🆕 新しい役を追加")
with st.expander("新規追加"):
    add_name = st.text_input("新しい役名", "新規役", key="add_name")
    add_score = st.number_input("新しいスコア", 100, key="add_score")
    c1, c2, c3 = st.columns(3)
    p_add1 = st.text_input("左図柄", "7️⃣", key="p_add1")
    p_add2 = st.text_input("中図柄", "7️⃣", key="p_add2")
    p_add3 = st.text_input("右図柄", "7️⃣", key="p_add3")
    if st.button("役を追加する"):
        new_payouts.append({"name": add_name, "score": add_score, "pattern": [p_add1, p_add2, p_add3]})
        st.success("追加しました！")
        st.rerun()

# 保存処理
st.write("---")
col_save, col_reset = st.columns([1, 1])
with col_save:
    if st.button("💾 設定を保存して反映する", use_container_width=True):
        # 図柄文字列をリストに戻す
        final_symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
        if not final_symbols:
            st.error("図柄は少なくとも1つ以上必要です。")
        else:
            new_config = {"symbols": final_symbols, "payouts": new_payouts}
            st.session_state.slot_config_edit = new_config
            storage.set_item("slot_config", new_config)
            # 実行ページ用のセッション状態も更新
            if "slot_config" in st.session_state:
                st.session_state.slot_config = new_config
            st.success("設定を保存しました！スロットページで確認してください。")
            st.balloons()

with col_reset:
    if st.button("🚨 デフォルトに戻す", use_container_width=True):
        default_config = {"symbols": DEFAULT_SYMBOLS, "payouts": DEFAULT_PAYOUTS}
        st.session_state.slot_config_edit = default_config
        storage.set_item("slot_config", default_config)
        if "slot_config" in st.session_state:
            st.session_state.slot_config = default_config
        st.success("デフォルト設定にリセットしました。")
        st.rerun()

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
