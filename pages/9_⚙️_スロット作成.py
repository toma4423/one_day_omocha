import json

import pandas as pd
import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.slot import (
    DEFAULT_PAYOUTS,
    DEFAULT_SLOT_NAME,
    DEFAULT_SYMBOLS,
    calculate_probabilities,
    get_slot_config,
    solve_weights_from_targets,
)
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

# 逆算用ターゲット率の保持
if "slot_targets" not in st.session_state:
    st.session_state.slot_targets = {}
if "slot_target_hit_rate" not in st.session_state:
    st.session_state.slot_target_hit_rate = 10.0

st.title("⚙️ スロットカスタマイズ")

# --- 設定：名前 ---
st.subheader("📝 基本設定")
slot_name = st.text_input("スロットの名前", st.session_state.slot_config_edit.get("name", DEFAULT_SLOT_NAME))

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

st.info("スロットの図柄や出現率をカスタマイズできます。数字の「ID」が図柄の識別に使われます。")

# --- 図柄の編集 ---
st.subheader("🖼️ 図柄（シンボル）の編集")
st.write("数字のID、表示用テキスト、オプションの画像URLを設定します。")

new_symbols = []
symbol_list = st.session_state.slot_config_edit["symbols"]
for i, symbol in enumerate(symbol_list):
    col_id, col_sym, col_url, col_del = st.columns([1, 2, 4, 1])
    with col_id:
        s_id = st.number_input(
            "ID", value=int(symbol["id"]), min_value=1, key=f"s_id_{i}", label_visibility="collapsed"
        )
    with col_sym:
        s_char = st.text_input(
            "表示テキスト", symbol["char"], key=f"s_char_{i}", label_visibility="collapsed", placeholder="表示テキスト"
        )
    with col_url:
        s_url = st.text_input(
            "画像URL (任意)",
            symbol.get("image_url", ""),
            key=f"s_url_{i}",
            label_visibility="collapsed",
            placeholder="https://... (画像URL)",
        )
    with col_del:
        if st.button("🗑️", key=f"s_del_{i}"):
            st.session_state.slot_config_edit["symbols"].pop(i)
            st.rerun()

    if s_url:
        st.image(s_url, width=50)
    else:
        st.markdown(f"<h3 style='margin:0;'>{s_char}</h3>", unsafe_allow_html=True)

    new_symbols.append(
        {"id": s_id, "char": s_char, "weight": symbol.get("weight", 1.0), "image_url": s_url if s_url else None}
    )

# 新しい図柄を追加
st.write("🆕 新しい図柄を追加")
c1, c2, c3, c4 = st.columns([1, 2, 4, 1])
with c1:
    # 現在の最大ID+1をデフォルトにする
    max_id = max([s["id"] for s in new_symbols]) if new_symbols else 0
    add_s_id = st.number_input("新ID", value=max_id + 1, min_value=1, key="add_s_id", label_visibility="collapsed")
with c2:
    add_s_char = st.text_input("表示", "💎", key="add_s_char", label_visibility="collapsed")
with c3:
    add_s_url = st.text_input("画像URL", "", key="add_s_url", label_visibility="collapsed", placeholder="https://...")
with c4:
    if st.button("➕", key="add_s_btn"):
        st.session_state.slot_config_edit["symbols"].append(
            {"id": add_s_id, "char": add_s_char, "weight": 1.0, "image_url": add_s_url if add_s_url else None}
        )
        st.rerun()

# --- 役の編集 ---
st.write("---")
st.subheader("💰 役と出現率の設定")
st.write("各役の名称、図柄パターン（IDで選択）、スコア、目標出現確率を設定します。")

# 全体確率の調整
st.session_state.slot_target_hit_rate = st.slider(
    "全体の合算当り確率 (%)", 0.1, 95.0, float(st.session_state.slot_target_hit_rate), step=0.1
)

new_payouts = []
payout_list = st.session_state.slot_config_edit["payouts"]
# 図柄のIDと表示名のマップを作成
symbol_options_map = {s["id"]: f"{s['id']}: {s['char']}" for s in new_symbols}
symbol_ids = ["ANY"] + sorted(list(symbol_options_map.keys()))


def get_label(sid):
    if sid == "ANY":
        return "ANY (何でも)"
    return symbol_options_map.get(sid, str(sid))


for i, payout in enumerate(payout_list):
    with st.expander(f"役 {i + 1}: {payout['name']}"):
        col_name, col_score, col_target = st.columns([2, 1, 1])
        with col_name:
            p_name = st.text_input("役名", payout["name"], key=f"p_name_{i}")
        with col_score:
            p_score = st.number_input("スコア", value=int(payout["score"]), min_value=0, step=1, key=f"p_score_{i}")
        with col_target:
            st.session_state.slot_targets[p_name] = st.number_input(
                "目標確率 (%)",
                value=float(st.session_state.slot_targets.get(p_name, 1.0 if i == 0 else 0.0)),
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                key=f"p_target_{i}",
            )

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            p_1 = st.selectbox(
                "左リール (ID)",
                symbol_ids,
                index=symbol_ids.index(payout["pattern"][0]) if payout["pattern"][0] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_1_{i}",
            )
        with col_p2:
            p_2 = st.selectbox(
                "中リール (ID)",
                symbol_ids,
                index=symbol_ids.index(payout["pattern"][1]) if payout["pattern"][1] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_2_{i}",
            )
        with col_p3:
            p_3 = st.selectbox(
                "右リール (ID)",
                symbol_ids,
                index=symbol_ids.index(payout["pattern"][2]) if payout["pattern"][2] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_3_{i}",
            )

        if st.button("この役を削除する", key=f"p_del_btn_{i}"):
            st.session_state.slot_config_edit["payouts"].pop(i)
            st.rerun()

        new_payouts.append({"name": p_name, "score": p_score, "pattern": [p_1, p_2, p_3]})

# 新しい役を追加
st.write("🆕 新しい役を追加")
with st.expander("新規追加"):
    add_name = st.text_input("新しい役名", "新規役", key="add_name")
    add_score = st.number_input("新しいスコア", 100, key="add_score")
    ca1, ca2, ca3 = st.columns(3)
    with ca1:
        p_add1 = st.selectbox("左図柄 ID", symbol_ids, format_func=get_label, key="p_add1")
    with ca2:
        p_add2 = st.selectbox("中図柄 ID", symbol_ids, format_func=get_label, key="p_add2")
    with ca3:
        p_add3 = st.selectbox("右図柄 ID", symbol_ids, format_func=get_label, key="p_add3")
    if st.button("役を追加する"):
        st.session_state.slot_config_edit["payouts"].append(
            {"name": add_name, "score": add_score, "pattern": [p_add1, p_add2, p_add3]}
        )
        st.rerun()

# --- 確率計算と反映 ---
st.write("---")
st.subheader("🧮 確率計算と反映")
if st.button("自動計算を実行してプレビュー", use_container_width=True):
    updated_symbols = solve_weights_from_targets(
        new_symbols, new_payouts, st.session_state.slot_targets, st.session_state.slot_target_hit_rate
    )
    st.session_state.slot_config_edit["symbols"] = updated_symbols
    st.success("重みを計算しました。")
    st.rerun()

probs = calculate_probabilities(st.session_state.slot_config_edit["symbols"], new_payouts)
col_res1, col_res2 = st.columns(2)
with col_res1:
    st.metric("実際の合計当り確率", f"{probs['total_hit_rate']:.2f}%")
with col_res2:
    st.metric("ハズレ確率", f"{probs['miss_rate']:.2f}%")

df_probs = pd.DataFrame(probs["hit_rates"])
if not df_probs.empty:
    df_probs.columns = ["役名", "出現確率 (%)"]
    st.table(df_probs)

# 保存処理
st.write("---")
col_save, col_reset = st.columns([1, 1])
with col_save:
    if st.button("💾 この設定を保存して反映する", use_container_width=True):
        if not slot_name:
            st.error("スロットの名前を入力してください。")
        else:
            final_config = {
                "name": slot_name,
                "symbols": st.session_state.slot_config_edit["symbols"],
                "payouts": new_payouts,
            }
            st.session_state.slot_config_edit = final_config
            storage.set_item("slot_config", final_config)
            if "slot_config" in st.session_state:
                st.session_state.slot_config = final_config
            st.success("設定を保存しました！")
            st.balloons()

with col_reset:
    if st.button("🚨 デフォルトに戻す", use_container_width=True):
        default_config = {"name": DEFAULT_SLOT_NAME, "symbols": DEFAULT_SYMBOLS, "payouts": DEFAULT_PAYOUTS}
        st.session_state.slot_config_edit = default_config
        storage.set_item("slot_config", default_config)
        st.rerun()

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
