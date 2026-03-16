from typing import Any

import polars as pl
import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.slot import (
    DEFAULT_PAYOUTS,
    DEFAULT_SYMBOLS,
    SlotConfig,
    SlotPayout,
    SlotSymbol,
    calculate_probabilities,
    get_slot_config,
    validate_slot_config,
)
from src.utils.storage import SafeStorage
from src.utils.styles import (
    render_donation_box,
    render_page_header,
    render_storage_controls,
    wait_for_storage_load,
)

st.set_page_config(page_title="スロット作成 [β]", page_icon="⚙️", layout="wide")

# グローバルスタイルの適用
render_page_header()

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# 設定のロード (堅牢な初期化)
if "slot_config_edit" not in st.session_state:
    saved_config = wait_for_storage_load(storage, "slot_config", "_slot_creation_initialized")
    try:
        st.session_state.slot_config_edit = get_slot_config(saved_config)
    except Exception:
        st.session_state.slot_config_edit = get_slot_config(None)
    st.rerun()
    st.stop()

# 二重の安全策: 初期化が完了していない場合はここで停止
if "slot_config_edit" not in st.session_state:
    st.stop()

config: SlotConfig = st.session_state.slot_config_edit

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
        config.name,
    )
    if slot_name != config.name:
        config.name = slot_name

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

    updated_symbols = []
    to_delete_symbol = None

    for i, symbol in enumerate(config.symbols):
        col_id, col_sym, col_url, col_del = st.columns([1, 2, 4, 1])
        with col_id:
            s_id = st.number_input(
                "ID", value=int(symbol.id), min_value=1, key=f"s_id_{i}", label_visibility="collapsed"
            )
        with col_sym:
            s_char = st.text_input("ラベル", symbol.char, key=f"s_char_{i}", label_visibility="collapsed")
        with col_url:
            s_url = st.text_input(
                "URL", symbol.image_url if symbol.image_url else "", key=f"s_url_{i}", label_visibility="collapsed"
            )
        with col_del:
            if st.button("🗑️", key=f"s_del_{i}"):
                to_delete_symbol = i

        updated_symbols.append(
            SlotSymbol(id=s_id, char=s_char, weight=symbol.weight, image_url=s_url if s_url else None)
        )

    if to_delete_symbol is not None:
        config.symbols.pop(to_delete_symbol)
        st.rerun()

    if updated_symbols != config.symbols:
        config.symbols = updated_symbols

    st.write("🆕 **新しい図柄を追加**")
    c1, c2, c3, c4 = st.columns([1, 2, 4, 1])
    with c1:
        max_id = max([s.id for s in config.symbols]) if config.symbols else 0
        add_s_id = st.number_input("新ID", value=max_id + 1, min_value=1, key="add_s_id", label_visibility="collapsed")
    with c2:
        add_s_char = st.text_input("新ラベル", "💎", key="add_s_char", label_visibility="collapsed")
    with c3:
        add_s_url = st.text_input("新URL", "", key="add_s_url", label_visibility="collapsed")
    with c4:
        if st.button("➕", key="add_s_btn"):
            config.symbols.append(
                SlotSymbol(id=add_s_id, char=add_s_char, weight=1.0, image_url=add_s_url if add_s_url else None)
            )
            st.rerun()

st.write("")

# --- 役の編集 ---
st.subheader("💰 役と出現率の設定")
with st.container(border=True):
    st.info("どの図柄が揃ったら当たりにするか、その確率はいくらかを設定します。")

    symbol_options_map = {s.id: f"{s.char}" for s in config.symbols}
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

    updated_payouts = []
    to_delete_payout = None

    for i, payout in enumerate(config.payouts):
        row_col1, row_col2, row_col3, row_col4, row_col5, row_col6 = st.columns([3, 2, 2, 2, 1.5, 0.5])

        with row_col1:
            p_name = st.text_input("役名", payout.name, key=f"p_name_{i}", label_visibility="collapsed")

        with row_col2:
            p_1 = st.selectbox(
                "左",
                symbol_ids,
                index=symbol_ids.index(payout.pattern[0]) if payout.pattern[0] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_1_{i}",
                label_visibility="collapsed",
            )

        with row_col3:
            p_2 = st.selectbox(
                "中",
                symbol_ids,
                index=symbol_ids.index(payout.pattern[1]) if payout.pattern[1] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_2_{i}",
                label_visibility="collapsed",
            )

        with row_col4:
            p_3 = st.selectbox(
                "右",
                symbol_ids,
                index=symbol_ids.index(payout.pattern[2]) if payout.pattern[2] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_3_{i}",
                label_visibility="collapsed",
            )

        with row_col5:
            current_denom = float(payout.denominator)
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
                to_delete_payout = i

        updated_payouts.append(SlotPayout(name=p_name, score=0, denominator=p_denom, pattern=[p_1, p_2, p_3]))

    if to_delete_payout is not None:
        config.payouts.pop(to_delete_payout)
        st.rerun()

    if updated_payouts != config.payouts:
        config.payouts = updated_payouts

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
            config.payouts.append(
                SlotPayout(name=add_name, score=0, denominator=add_denom, pattern=[p_add1, p_add2, p_add3])
            )
            st.rerun()

st.write("")

# --- 確率計算とプレビュー ---
st.subheader("🧮 確率計算とプレビュー")
with st.container(border=True):
    probs = calculate_probabilities(config)
    st.metric(
        "合計当り確率",
        f"{probs['total_hit_rate']:.2f}% (1/{100 / probs['total_hit_rate'] if probs['total_hit_rate'] > 0 else 0:.1f})",
    )

    st.write("📊 **現在の設定一覧**")
    df_probs = pl.DataFrame(probs["hit_rates"])
    if not df_probs.is_empty():
        df_probs = df_probs.with_columns(
            pl.col("denominator").map_elements(lambda x: f"1/{x}", return_dtype=pl.String).alias("1/N")
        ).select(
            [pl.col("name").alias("役名"), pl.col("1/N").alias("設定確率 (分母)"), pl.col("rate").alias("出現確率 (%)")]
        )
        st.table(df_probs)


# --- データの保存と読み込み ---
def on_load(data: Any) -> None:
    valid, msg = validate_slot_config(data)
    if valid:
        new_config = SlotConfig(**data)
        st.session_state.slot_config_edit = new_config
        # 読み込み時は即座に反映
        st.session_state.slot_config = new_config
    else:
        st.error(msg)


def on_save() -> None:
    if not slot_name:
        st.error("名前を入力してください")
    else:
        st.session_state.slot_config = config
        st.balloons()


render_storage_controls(
    storage=storage,
    storage_key="slot_config",
    current_data=config,
    on_load_callback=on_load,
    on_save_callback=on_save,
    file_prefix="slot_config",
    is_pydantic=True,
)

st.write("---")
if st.button("🚨 デフォルトに戻す", use_container_width=True):
    default_config = SlotConfig(symbols=DEFAULT_SYMBOLS, payouts=DEFAULT_PAYOUTS)
    st.session_state.slot_config_edit = default_config
    st.rerun()

# サイドバー
with st.sidebar:
    st.header("⚙️ 管理")
    st.info("設定はメインエリアの『データの管理』パネルから行えます。")

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
