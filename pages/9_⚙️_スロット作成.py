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
slot_name = st.text_input(
    "スロットの名前",
    st.session_state.slot_config_edit.get("name", DEFAULT_SLOT_NAME),
    help="スロット台の名称です。スロットページにタイトルとして表示されます。",
)

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
        help="現在のすべての設定を JSON ファイルとして自分のPC/スマホに保存します。",
    )

    # JSONロード
    uploaded_file = st.file_uploader(
        "設定JSONを読込",
        type="json",
        help="過去に保存した設定 JSON ファイルを読み込んで復元します。",
    )
    if uploaded_file is not None:
        if st.button("設定を復元する", use_container_width=True):
            try:
                data_load = json.load(uploaded_file)
                if "symbols" in data_load and "payouts" in data_load:
                    migrated_config = migrate_slot_config(data_load)
                    st.session_state.slot_config_edit = migrated_config
                    storage.set_item("slot_config", migrated_config)
                    if "slot_config" in st.session_state:
                        st.session_state.slot_config = migrated_config
                    st.success("設定を復元しました！")
                    st.rerun()
                else:
                    st.error("不正な設定ファイル形式です")
            except Exception:
                st.error("JSONの読み込みに失敗しました")
    st.write("---")

st.info(
    "スロットの図柄や出現率をカスタマイズできます。「図柄識別名」は役の判定に使用され、「画像URL」があれば優先的に表示されます。"
)

# --- 図柄の編集 ---
st.subheader("🖼️ 図柄（シンボル）の編集")
st.write("リールに出現する図柄の種類を定義します。")

# ヘッダー説明
hc1, hc2, hc3, hc4 = st.columns([1, 2, 4, 1])
hc1.caption("ID（識別番号）")
hc2.caption("表示テキスト")
hc3.caption("画像URL (オプション)")
hc4.caption("削除")

new_symbols = []
symbol_list = st.session_state.slot_config_edit["symbols"]
for i, symbol in enumerate(symbol_list):
    col_id, col_sym, col_url, col_del = st.columns([1, 2, 4, 1])
    with col_id:
        s_id = st.number_input(
            "ID",
            value=int(symbol["id"]),
            min_value=1,
            key=f"s_id_{i}",
            label_visibility="collapsed",
            help="図柄を一意に識別するための数字です。役の設定で使用します。",
        )
    with col_sym:
        s_char = st.text_input(
            "表示テキスト",
            symbol["char"],
            key=f"s_char_{i}",
            label_visibility="collapsed",
            placeholder="識別名",
            help="画像がない場合や、履歴画面で表示される文字です。",
        )
    with col_url:
        s_url = st.text_input(
            "画像URL",
            symbol.get("image_url", ""),
            key=f"s_url_{i}",
            label_visibility="collapsed",
            placeholder="https://... (画像URL)",
            help="インターネット上の画像URLを入力すると、リール上でその画像が表示されます。",
        )
    with col_del:
        if st.button("🗑️", key=f"s_del_{i}", help="この図柄をリストから削除します。"):
            st.session_state.slot_config_edit["symbols"].pop(i)
            st.rerun()

    # 画像プレビュー（URLがある場合）
    if s_url:
        try:
            st.image(s_url, width=50)
        except Exception:
            st.caption("⚠️ 画像読み込み失敗")
    else:
        st.markdown(f"<h3 style='margin:0; text-align:center;'>{s_char}</h3>", unsafe_allow_html=True)

    new_symbols.append(
        {"id": s_id, "char": s_char, "weight": symbol.get("weight", 1.0), "image_url": s_url if s_url else None}
    )

# 新しい図柄を追加
st.write("🆕 新しい図柄を追加")
c1, c2, c3, c4 = st.columns([1, 2, 4, 1])
with c1:
    max_id = max([s["id"] for s in new_symbols]) if new_symbols else 0
    add_s_id = st.number_input(
        "新ID",
        value=max_id + 1,
        min_value=1,
        key="add_s_id",
        label_visibility="collapsed",
        help="新しい図柄のIDです。",
    )
with c2:
    add_s_char = st.text_input(
        "表示", "💎", key="add_s_char", label_visibility="collapsed", help="新しい図柄の表示文字です。"
    )
with c3:
    add_s_url = st.text_input(
        "画像URL",
        "",
        key="add_s_url",
        label_visibility="collapsed",
        placeholder="https://...",
        help="新しい図柄の画像URLです。",
    )
with c4:
    if st.button("➕", key="add_s_btn", help="新しい図柄を上のリストに追加します。"):
        st.session_state.slot_config_edit["symbols"].append(
            {"id": add_s_id, "char": add_s_char, "weight": 1.0, "image_url": add_s_url if add_s_url else None}
        )
        st.rerun()

# --- 役の編集 ---
st.write("---")
st.subheader("💰 役と出現率の設定")
st.write("揃った時の「配当スコア」と「出現確率」を設定します。")

# 全体確率の調整
st.session_state.slot_target_hit_rate = st.slider(
    "全体の合算当り確率 (%)",
    0.1,
    95.0,
    float(st.session_state.slot_target_hit_rate),
    step=0.1,
    help="リールを回した際、いずれかの役が揃う合計の確率です。残りの確率は『ハズレ』になります。",
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
            p_name = st.text_input("役名", payout["name"], key=f"p_name_{i}", help="当たった時に表示される名前です。")
        with col_score:
            p_score = st.number_input(
                "スコア",
                value=int(payout["score"]),
                min_value=0,
                step=1,
                key=f"p_score_{i}",
                help="当たった時に加算される点数です。",
            )
        with col_target:
            st.session_state.slot_targets[p_name] = st.number_input(
                "目標確率 (%)",
                value=float(st.session_state.slot_targets.get(p_name, 1.0 if i == 0 else 0.0)),
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                key=f"p_target_{i}",
                help="この役がどれくらいの確率（％）で出現してほしいかの目標値です。",
            )

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            p_1 = st.selectbox(
                "左リール",
                symbol_ids,
                index=symbol_ids.index(payout["pattern"][0]) if payout["pattern"][0] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_1_{i}",
                help="一番左のリールに止まるべき図柄です。",
            )
        with col_p2:
            p_2 = st.selectbox(
                "中リール",
                symbol_ids,
                index=symbol_ids.index(payout["pattern"][1]) if payout["pattern"][1] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_2_{i}",
                help="真ん中のリールに止まるべき図柄です。",
            )
        with col_p3:
            p_3 = st.selectbox(
                "右リール",
                symbol_ids,
                index=symbol_ids.index(payout["pattern"][2]) if payout["pattern"][2] in symbol_ids else 0,
                format_func=get_label,
                key=f"p_3_{i}",
                help="一番右のリールに止まるべき図柄です。",
            )

        if st.button("この役を削除する", key=f"p_del_btn_{i}", help="この役の設定を削除します。"):
            st.session_state.slot_config_edit["payouts"].pop(i)
            st.rerun()

        new_payouts.append({"name": p_name, "score": p_score, "pattern": [p_1, p_2, p_3]})

# 新しい役を追加
st.write("🆕 新しい役を追加")
with st.expander("新規役の追加フォーム"):
    add_name = st.text_input("新しい役名", "新規役", key="add_name", help="追加する役の名称。")
    add_score = st.number_input("新しいスコア", 100, key="add_score", help="追加する役の配当点数。")
    ca1, ca2, ca3 = st.columns(3)
    with ca1:
        p_add1 = st.selectbox("左図柄 ID", symbol_ids, format_func=get_label, key="p_add1")
    with ca2:
        p_add2 = st.selectbox("中図柄 ID", symbol_ids, format_func=get_label, key="p_add2")
    with ca3:
        p_add3 = st.selectbox("右図柄 ID", symbol_ids, format_func=get_label, key="p_add3")
    if st.button("役を追加する", use_container_width=True, help="上の内容で新しい役をリストに追加します。"):
        st.session_state.slot_config_edit["payouts"].append(
            {"name": add_name, "score": add_score, "pattern": [p_add1, p_add2, p_add3]}
        )
        st.rerun()

# --- 確率計算と反映 ---
st.write("---")
st.subheader("🧮 確率計算と反映")
st.write("入力した「目標確率」に合わせて、システムが内部的な重みを自動計算します。")

if st.button(
    "自動計算を実行してプレビュー",
    use_container_width=True,
    help="上の設定に基づき、最適な図柄の出現率を逆算します。保存前に必ず一度実行してください。",
):
    updated_symbols = solve_weights_from_targets(
        new_symbols, new_payouts, st.session_state.slot_targets, st.session_state.slot_target_hit_rate
    )
    st.session_state.slot_config_edit["symbols"] = updated_symbols
    st.success("重みを計算しました！下の表で実際の確率を確認し、問題なければ保存してください。")
    st.rerun()

# 理論値の表示
probs = calculate_probabilities(st.session_state.slot_config_edit["symbols"], new_payouts)
col_res1, col_res2 = st.columns(2)
with col_res1:
    st.metric(
        "実際の合計当り確率",
        f"{probs['total_hit_rate']:.2f}%",
        help="現在の設定で、いずれかの役が揃う理論上の確率です。",
    )
with col_res2:
    st.metric("ハズレ確率", f"{probs['miss_rate']:.2f}%", help="何も揃わない理論上の確率です。")

df_probs = pd.DataFrame(probs["hit_rates"])
if not df_probs.empty:
    df_probs.columns = ["役名", "出現確率 (%)"]
    st.table(df_probs)

# 保存処理
st.write("---")
col_save, col_reset = st.columns([1, 1])
with col_save:
    if st.button(
        "💾 この設定を保存して反映する",
        use_container_width=True,
        help="現在のすべての設定をブラウザに保存し、スロット本体に反映します。",
    ):
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
            st.success("設定を保存しました！スロットページで確認してください。")
            st.balloons()

with col_reset:
    if st.button(
        "🚨 デフォルトに戻す",
        use_container_width=True,
        help="すべてのカスタマイズを破棄し、初期の標準設定に戻します。",
    ):
        default_config = {"name": DEFAULT_SLOT_NAME, "symbols": DEFAULT_SYMBOLS, "payouts": DEFAULT_PAYOUTS}
        st.session_state.slot_config_edit = default_config
        storage.set_item("slot_config", default_config)
        st.rerun()

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
