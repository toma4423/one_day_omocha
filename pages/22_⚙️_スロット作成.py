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
    migrate_slot_config,
    solve_weights_from_targets,
    validate_slot_config,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_page_header
from src.utils.time import get_jst_now

st.set_page_config(page_title="スロット作成 [β]", page_icon="⚙️", layout="wide")

# グローバルスタイルの適用
render_page_header()

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

st.title("⚙️ スロットカスタマイズ [β]")

# --- 設定：名前 ---
with st.container(border=True):
    st.subheader("📝 基本設定")
    slot_name = st.text_input(
        "スロットの名前",
        st.session_state.slot_config_edit.get("name", DEFAULT_SLOT_NAME),
        help="スロット台の名称です。スロットページにタイトルとして表示されます。",
    )

st.write("")

# --- 図柄の編集 ---
st.subheader("🖼️ 図柄（シンボル）の編集")
with st.container(border=True):
    # ヘッダー説明
    hc1, hc2, hc3, hc4 = st.columns([1, 2, 4, 1])
    hc1.caption("ID")
    hc2.caption("管理用ラベル")
    hc3.caption("画像URL (オプション)")
    hc4.caption("削除")

    new_symbols = []
    symbol_list = st.session_state.slot_config_edit["symbols"]
    for i, symbol in enumerate(symbol_list):
        col_id, col_sym, col_url, col_del = st.columns([1, 2, 4, 1])
        with col_id:
            s_id = st.number_input(
                "ID", value=int(symbol["id"]), min_value=1, key=f"s_id_{i}", label_visibility="collapsed"
            )
        with col_sym:
            s_char = st.text_input("ラベル", symbol["char"], key=f"s_char_{i}", label_visibility="collapsed")
        with col_url:
            s_url = st.text_input("URL", symbol.get("image_url", ""), key=f"s_url_{i}", label_visibility="collapsed")
        with col_del:
            if st.button("🗑️", key=f"s_del_{i}"):
                st.session_state.slot_config_edit["symbols"].pop(i)
                st.rerun()
        new_symbols.append(
            {"id": s_id, "char": s_char, "weight": symbol.get("weight", 1.0), "image_url": s_url if s_url else None}
        )

    st.write("🆕 **新しい図柄を追加**")
    c1, c2, c3, c4 = st.columns([1, 2, 4, 1])
    with c1:
        max_id = max([s["id"] for s in new_symbols]) if new_symbols else 0
        add_s_id = st.number_input("新ID", value=max_id + 1, min_value=1, key="add_s_id", label_visibility="collapsed")
    with c2:
        add_s_char = st.text_input("新ラベル", "💎", key="add_s_char", label_visibility="collapsed")
    with c3:
        add_s_url = st.text_input("新URL", "", key="add_s_url", label_visibility="collapsed")
    with c4:
        if st.button("➕", key="add_s_btn"):
            st.session_state.slot_config_edit["symbols"].append(
                {"id": add_s_id, "char": add_s_char, "weight": 1.0, "image_url": add_s_url if add_s_url else None}
            )
            st.rerun()

st.write("")

# --- 役の編集 ---
st.subheader("💰 役と出現率の設定")
with st.container(border=True):
    st.session_state.slot_target_hit_rate = st.slider(
        "全体の合算当り確率 (%)", 0.1, 95.0, float(st.session_state.slot_target_hit_rate), step=0.1
    )

    new_payouts = []
    symbol_options_map = {s["id"]: f"{s['id']}: {s['char']}" for s in new_symbols}
    symbol_ids = ["ANY"] + sorted(list(symbol_options_map.keys()))

    def get_label(sid):
        return "ANY (何でも)" if sid == "ANY" else symbol_options_map.get(sid, str(sid))

    for i, payout in enumerate(st.session_state.slot_config_edit["payouts"]):
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
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                p_1 = st.selectbox(
                    "左",
                    symbol_ids,
                    index=symbol_ids.index(payout["pattern"][0]) if payout["pattern"][0] in symbol_ids else 0,
                    format_func=get_label,
                    key=f"p_1_{i}",
                )
            with cp2:
                p_2 = st.selectbox(
                    "中",
                    symbol_ids,
                    index=symbol_ids.index(payout["pattern"][1]) if payout["pattern"][1] in symbol_ids else 0,
                    format_func=get_label,
                    key=f"p_2_{i}",
                )
            with cp3:
                p_3 = st.selectbox(
                    "右",
                    symbol_ids,
                    index=symbol_ids.index(payout["pattern"][2]) if payout["pattern"][2] in symbol_ids else 0,
                    format_func=get_label,
                    key=f"p_3_{i}",
                )
            if st.button("この役を削除", key=f"p_del_btn_{i}"):
                st.session_state.slot_config_edit["payouts"].pop(i)
                st.rerun()
            new_payouts.append({"name": p_name, "score": p_score, "pattern": [p_1, p_2, p_3]})

    st.write("🆕 **新しい役を追加**")
    with st.expander("新規役の追加フォーム"):
        add_name = st.text_input("新しい役名", "新規役", key="add_name")
        add_score = st.number_input("新しいスコア", 100, key="add_score")
        ca1, ca2, ca3 = st.columns(3)
        with ca1:
            p_add1 = st.selectbox("左図柄 ID", symbol_ids, format_func=get_label, key="p_add1")
        with ca2:
            p_add2 = st.selectbox("中図柄 ID", symbol_ids, format_func=get_label, key="p_add2")
        with ca3:
            p_add3 = st.selectbox("右図柄 ID", symbol_ids, format_func=get_label, key="p_add3")
        if st.button("役を追加する", use_container_width=True):
            st.session_state.slot_config_edit["payouts"].append(
                {"name": add_name, "score": add_score, "pattern": [p_add1, p_add2, p_add3]}
            )
            st.rerun()

st.write("")

# --- 確率計算と反映 ---
st.subheader("🧮 確率計算と反映")
with st.container(border=True):
    if st.button("自動計算を実行してプレビュー", use_container_width=True, type="primary"):
        updated_symbols = solve_weights_from_targets(
            new_symbols, new_payouts, st.session_state.slot_targets, st.session_state.slot_target_hit_rate
        )
        st.session_state.slot_config_edit["symbols"] = updated_symbols
        st.success("計算完了！問題なければ保存してください。")
        st.rerun()

    probs = calculate_probabilities(st.session_state.slot_config_edit["symbols"], new_payouts)
    cr1, cr2 = st.columns(2)
    with cr1:
        st.metric("合計当り確率", f"{probs['total_hit_rate']:.2f}%")
    with cr2:
        st.metric("ハズレ確率", f"{probs['miss_rate']:.2f}%")
    df_probs = pd.DataFrame(probs["hit_rates"])
    if not df_probs.empty:
        df_probs.columns = ["役名", "出現確率 (%)"]
        st.table(df_probs)

st.write("---")
col_save, col_reset = st.columns(2)
with col_save:
    if st.button("💾 設定を保存して反映", use_container_width=True, type="primary"):
        if not slot_name:
            st.error("名前を入力してください")
        else:
            final_config = {
                "name": slot_name,
                "symbols": st.session_state.slot_config_edit["symbols"],
                "payouts": new_payouts,
            }
            storage.set_item("slot_config", final_config)
            st.session_state.slot_config = final_config
            st.success("保存しました！")
            st.balloons()
            if st.button("🎰 スロットページへ移動", use_container_width=True):
                st.switch_page("pages/15_🎰_スロット.py")

with col_reset:
    if st.button("🚨 デフォルトに戻す", use_container_width=True):
        default_config = {"name": DEFAULT_SLOT_NAME, "symbols": DEFAULT_SYMBOLS, "payouts": DEFAULT_PAYOUTS}
        storage.set_item("slot_config", default_config)
        st.rerun()

# サイドバー
with st.sidebar:
    st.header("💾 データ管理")
    json_str = json.dumps(st.session_state.slot_config_edit, indent=2, ensure_ascii=False)
    st.download_button(
        "📥 JSON保存",
        data=json_str,
        file_name=f"slot_{get_jst_now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True,
    )
    uploaded_file = st.file_uploader("📤 JSON読込", type="json")
    if uploaded_file and st.button("🚀 適用", use_container_width=True):
        try:
            data = migrate_slot_config(json.load(uploaded_file))
            valid, msg = validate_slot_config(data)
            if valid:
                storage.set_item("slot_config", data)
                st.rerun()
            else:
                st.error(msg)
        except Exception as e:
            st.error(f"失敗: {e}")

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
