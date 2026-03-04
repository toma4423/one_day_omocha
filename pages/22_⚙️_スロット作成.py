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

st.title("⚙️ スロットカスタマイズ [β]")

# --- 初心者向けガイド ---
with st.expander("📖 はじめてのスロット作りガイド（クリックで展開）", expanded=False):
    st.markdown("""
    ### 🎰 自分だけのスロットを作るコツ
    このページでは、各役がどれくらいの確率で当たるかを自由に設定できます。
    
    #### 1. 「分母 (1/N)」ってなに？
    当たりやすさを決める数字です。**「数字が小さいほど当たりやすい」**と覚えてください。
    - **10.0** と入力 ➡ 10回に1回くらい当たります
    - **256.0** と入力 ➡ 256回に1回くらい当たります

    #### 2. おすすめの定番設定
    迷ったらこの数字を入れてみてください：
    - **当たりやすい役**: 1/7.0 〜 1/15.0
    - **ちょっと珍しい役**: 1/30.0 〜 1/100.0
    - **大当たり（777）**: 1/200.0 〜 1/300.0
    """)

# --- 設定：名前 ---
with st.container(border=True):
    st.subheader("📝 基本設定")
    slot_name = st.text_input(
        "スロットの名前",
        st.session_state.slot_config_edit.get("name", DEFAULT_SLOT_NAME),
    )

st.write("")

# --- 図柄の編集 ---
st.subheader("🖼️ 図柄（シンボル）の編集")
with st.container(border=True):
    st.info("リールに表示される図柄を定義します。")
    hc1, hc2, hc3, hc4 = st.columns([1, 2, 4, 1])
    hc1.caption("ID")
    hc2.caption("管理用ラベル")
    hc3.caption("画像URL (オプション)")
    hc4.caption("削除")

    current_symbols = st.session_state.slot_config_edit["symbols"]
    updated_symbols = []

    for i, symbol in enumerate(current_symbols):
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

        updated_symbols.append(
            {"id": s_id, "char": s_char, "weight": symbol.get("weight", 1.0), "image_url": s_url if s_url else None}
        )

    if updated_symbols != current_symbols:
        st.session_state.slot_config_edit["symbols"] = updated_symbols

    st.write("🆕 **新しい図柄を追加**")
    c1, c2, c3, c4 = st.columns([1, 2, 4, 1])
    with c1:
        max_id = max([s["id"] for s in updated_symbols]) if updated_symbols else 0
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
    st.info("どの図柄が揃ったら当たりにするか、その確率はいくらかを設定します。")

    current_payouts = st.session_state.slot_config_edit["payouts"]
    updated_payouts = []

    symbol_options_map = {s["id"]: f"{s['char']}" for s in updated_symbols}
    symbol_ids = ["ANY"] + sorted(list(symbol_options_map.keys()))

    def get_label(sid):
        return "ANY" if sid == "ANY" else f"{sid}: {symbol_options_map.get(sid, str(sid))}"

    # ヘッダー
    h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 1])
    h1.caption("役名")
    h2.caption("左リール")
    h3.caption("中リール")
    h4.caption("右リール")
    h5.caption("確率(1/N)")

    for i, payout in enumerate(current_payouts):
        row_col1, row_col2, row_col3, row_col4, row_col5, row_col6 = st.columns([3, 2, 2, 2, 1.5, 0.5])

        with row_col1:
            p_name = st.text_input("役名", payout["name"], key=f"p_name_{i}", label_visibility="collapsed")

        with row_col2:
            p_1 = st.selectbox(
                "左",
                symbol_ids,
                index=symbol_ids.index(payout["pattern"][0]) if payout["pattern"][0] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_1_{i}",
                label_visibility="collapsed",
            )

        with row_col3:
            p_2 = st.selectbox(
                "中",
                symbol_ids,
                index=symbol_ids.index(payout["pattern"][1]) if payout["pattern"][1] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_2_{i}",
                label_visibility="collapsed",
            )

        with row_col4:
            p_3 = st.selectbox(
                "右",
                symbol_ids,
                index=symbol_ids.index(payout["pattern"][2]) if payout["pattern"][2] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_3_{i}",
                label_visibility="collapsed",
            )

        with row_col5:
            current_denom = float(payout.get("denominator", 10.0))
            p_denom = st.number_input(
                "分母",
                value=max(current_denom, 1.1),
                min_value=1.1,
                step=0.1,
                key=f"p_denom_{i}",
                label_visibility="collapsed",
            )

        with row_col6:
            if st.button("🗑️", key=f"p_del_btn_{i}", help="この役を削除"):
                st.session_state.slot_config_edit["payouts"].pop(i)
                st.rerun()

        updated_payouts.append({"name": p_name, "score": 0, "denominator": p_denom, "pattern": [p_1, p_2, p_3]})

    if updated_payouts != current_payouts:
        st.session_state.slot_config_edit["payouts"] = updated_payouts

    st.write("---")
    st.write("🆕 **新しい役を追加**")
    ca1, ca2, ca3, ca4, ca5, ca6 = st.columns([3, 2, 2, 2, 1.5, 0.5])
    with ca1:
        add_name = st.text_input(
            "新規役名", "新規役", key="add_name", label_visibility="collapsed", placeholder="役名を入力"
        )
    with ca2:
        p_add1 = st.selectbox("左ID", symbol_ids, format_func=get_label, key="p_add1", label_visibility="collapsed")
    with ca3:
        p_add2 = st.selectbox("中ID", symbol_ids, format_func=get_label, key="p_add2", label_visibility="collapsed")
    with ca4:
        p_add3 = st.selectbox("右ID", symbol_ids, format_func=get_label, key="p_add3", label_visibility="collapsed")
    with ca5:
        add_denom = st.number_input(
            "新規分母", value=100.0, min_value=1.1, key="add_denom", label_visibility="collapsed"
        )
    with ca6:
        if st.button("➕", key="add_p_btn"):
            st.session_state.slot_config_edit["payouts"].append(
                {"name": add_name, "score": 0, "denominator": add_denom, "pattern": [p_add1, p_add2, p_add3]}
            )
            st.rerun()

st.write("")

# --- 確率計算とプレビュー ---
st.subheader("🧮 確率計算とプレビュー")
with st.container(border=True):
    probs = calculate_probabilities(
        st.session_state.slot_config_edit["symbols"], st.session_state.slot_config_edit["payouts"]
    )
    st.metric(
        "合計当り確率",
        f"{probs['total_hit_rate']:.2f}% (1/{100 / probs['total_hit_rate'] if probs['total_hit_rate'] > 0 else 0:.1f})",
    )

    st.write("📊 **現在の設定一覧**")
    df_probs = pd.DataFrame(probs["hit_rates"])
    if not df_probs.empty:
        df_probs["1/N"] = df_probs["denominator"].apply(lambda x: f"1/{x}")
        df_probs = df_probs[["name", "1/N", "rate"]]
        df_probs.columns = ["役名", "設定確率 (分母)", "出現確率 (%)"]
        st.table(df_probs)

# --- データの保存と読み込み ---
st.write("---")
with st.container(border=True):
    st.subheader("📁 データの保存と読み込み")
    c1, c2 = st.columns(2)
    with c1:
        json_str = json.dumps(st.session_state.slot_config_edit, indent=2, ensure_ascii=False)
        st.download_button(
            "📥 設定をJSONで保存",
            json_str,
            f"slot_{get_jst_now().strftime('%Y%m%d')}.json",
            "application/json",
            use_container_width=True,
        )
    with c2:
        uploaded_file = st.file_uploader("📤 設定JSONを読み込む", type="json", label_visibility="collapsed")
        if uploaded_file and st.button("反映実行", use_container_width=True):
            try:
                data = migrate_slot_config(json.load(uploaded_file))
                valid, msg = validate_slot_config(data)
                if valid:
                    st.session_state.slot_config_edit = data
                    storage.set_item("slot_config", data)
                    st.success("反映しました！")
                    st.rerun()
                else:
                    st.error(msg)
            except Exception as e:
                st.error(f"失敗: {e}")

st.write("---")
col_save, col_reset = st.columns(2)
with col_save:
    if st.button("💾 現在の設定をスロット本体に反映", use_container_width=True, type="primary"):
        if not slot_name:
            st.error("名前を入力してください")
        else:
            final_config = {
                "name": slot_name,
                "symbols": st.session_state.slot_config_edit["symbols"],
                "payouts": st.session_state.slot_config_edit["payouts"],
            }
            storage.set_item("slot_config", final_config)
            st.session_state.slot_config = final_config
            st.success("反映しました！")
            st.balloons()

with col_reset:
    if st.button("🚨 デフォルトに戻す", use_container_width=True):
        default_config = {"name": DEFAULT_SLOT_NAME, "symbols": DEFAULT_SYMBOLS, "payouts": DEFAULT_PAYOUTS}
        st.session_state.slot_config_edit = default_config
        storage.set_item("slot_config", default_config)
        st.rerun()

# サイドバー
with st.sidebar:
    st.header("⚙️ 管理")
    st.info("設定はメインエリアの『保存と読み込み』から行えます。")

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
