import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.parallel_counter import (
    add_counter,
    migrate_parallel_counter_data,
    remove_counter,
    update_counter_name,
    update_counter_value,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box

st.set_page_config(page_title="並列カウンター", page_icon="🔢", layout="wide")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# セッション状態の初期化
if "parallel_counters" not in st.session_state:
    saved_data = storage.get_item("parallel_counters", is_json=True)
    st.session_state.parallel_counters = migrate_parallel_counter_data(saved_data)

# 前回更新した ID を保持（アニメーション制御用）
if "last_updated_id" not in st.session_state:
    st.session_state.last_updated_id = None

# カスタム CSS の読み込み
try:
    with open("src/assets/counter/style.css", encoding="utf-8") as f:
        counter_css = f.read()
except Exception:
    counter_css = ""

# Streamlitのボタンスタイルをよりカードに馴染むよう調整
st.markdown(f"<style>{counter_css}</style>", unsafe_allow_html=True)
st.markdown(
    """
    <style>
    /* Streamlitボタンのカスタマイズ */
    div[data-testid="stVerticalBlock"] div[data-testid="stColumn"] .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
        height: 50px !important;
    }
    .plus-btn > div > button {
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
    }
    .plus-btn > div > button:hover {
        background-color: #0056b3 !important;
        transform: scale(1.05);
    }
    .minus-btn > div > button {
        background-color: #f8f9fa !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
    }
    .minus-btn > div > button:hover {
        background-color: #e2e6ea !important;
    }
    .reset-btn > div > button, .del-btn > div > button {
        height: 35px !important;
        font-size: 14px !important;
        border-radius: 8px !important;
    }
    /* アニメーション用のクラス付与（簡易実装） */
    .pulse-effect {
        animation: pulse-animation 0.4s ease-out;
    }
    @keyframes pulse-animation {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); color: #007bff; }
        100% { transform: scale(1); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; font-weight: 900; color: #333;'>🔢 並列カウンター</h1>", unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: #777;'>複数の項目を同時にカウント。変更は自動的にブラウザに保存されます。</p>",
    unsafe_allow_html=True,
)

# ツールバー（上部）
col_actions, col_empty = st.columns([1, 4])
with col_actions:
    if st.button("➕ カウンターを追加", use_container_width=True, type="primary"):
        st.session_state.parallel_counters = add_counter(st.session_state.parallel_counters)
        storage.set_item("parallel_counters", st.session_state.parallel_counters)
        st.rerun()

st.write("")

# カウンターの表示
if not st.session_state.parallel_counters:
    st.info("カウンターがありません。「カウンターを追加」ボタンから作成してください。")
else:
    # 3列のグリッド
    cols = st.columns(3)

    for i, counter in enumerate(st.session_state.parallel_counters):
        col_idx = i % 3
        with cols[col_idx]:
            # カード開始
            with st.container(border=True):
                # 名称入力
                st.markdown("<div class='counter-title-input'>", unsafe_allow_html=True)
                new_name = st.text_input(
                    "名前",
                    value=counter["name"],
                    key=f"name_{counter['id']}",
                    label_visibility="collapsed",
                    placeholder="項目名を入力...",
                )
                if new_name != counter["name"]:
                    st.session_state.parallel_counters = update_counter_name(
                        st.session_state.parallel_counters, counter["id"], new_name
                    )
                    storage.set_item("parallel_counters", st.session_state.parallel_counters)
                st.markdown("</div>", unsafe_allow_html=True)

                # 数値表示（更新直後はアニメーション用クラスを付与）
                pulse_class = "pulse-effect" if st.session_state.last_updated_id == counter["id"] else ""
                st.markdown(
                    f"<div class='counter-value-container {pulse_class}' style='text-align: center;'>"
                    f"{counter['value']}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                # 操作ボタン（増減）
                st.markdown("<div class='counter-button-group'>", unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                with b1:
                    st.markdown("<div class='minus-btn'>", unsafe_allow_html=True)
                    if st.button("− 減らす", key=f"minus_{counter['id']}", use_container_width=True):
                        st.session_state.parallel_counters = update_counter_value(
                            st.session_state.parallel_counters, counter["id"], -1
                        )
                        st.session_state.last_updated_id = counter["id"]  # アニメーション対象
                        storage.set_item("parallel_counters", st.session_state.parallel_counters)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with b2:
                    st.markdown("<div class='plus-btn'>", unsafe_allow_html=True)
                    if st.button("＋ 増やす", key=f"plus_{counter['id']}", use_container_width=True):
                        st.session_state.parallel_counters = update_counter_value(
                            st.session_state.parallel_counters, counter["id"], 1
                        )
                        st.session_state.last_updated_id = counter["id"]  # アニメーション対象
                        storage.set_item("parallel_counters", st.session_state.parallel_counters)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # フッター操作（リセット、削除）
                st.markdown("<div class='counter-footer'>", unsafe_allow_html=True)
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown("<div class='reset-btn'>", unsafe_allow_html=True)
                    if st.button("🔄 リセット", key=f"reset_{counter['id']}", use_container_width=True):
                        for item in st.session_state.parallel_counters:
                            if item["id"] == counter["id"]:
                                item["value"] = 0
                                break
                        st.session_state.last_updated_id = counter["id"]
                        storage.set_item("parallel_counters", st.session_state.parallel_counters)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with r2:
                    st.markdown("<div class='del-btn'>", unsafe_allow_html=True)
                    if st.button("🗑️ 削除", key=f"del_{counter['id']}", use_container_width=True):
                        st.session_state.parallel_counters = remove_counter(
                            st.session_state.parallel_counters, counter["id"]
                        )
                        st.session_state.last_updated_id = None
                        storage.set_item("parallel_counters", st.session_state.parallel_counters)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# 更新アニメーションのリセット用フラグ管理
if st.session_state.last_updated_id:
    # 描画後、少し待ってフラグをリセット（次のアクションまでアニメーションしないように）
    # ただしStreamlitの性質上、描画直後のリセットは rerun を伴うため慎重に行う
    # 今回は簡易的に、描画時点でクラスを付与する手法。
    pass

st.write("---")

# サイドバー設定
with st.sidebar:
    st.subheader("⚙️ 一括操作")
    if st.button("🔄 すべての値をリセット", use_container_width=True):
        for item in st.session_state.parallel_counters:
            item["value"] = 0
        st.session_state.last_updated_id = "all"
        storage.set_item("parallel_counters", st.session_state.parallel_counters)
        st.success("すべてリセットしました")
        st.rerun()

    if st.button("🗑️ すべてのカウンターを削除", use_container_width=True):
        if st.checkbox("本当に削除しますか？", key="del_confirm"):
            st.session_state.parallel_counters = []
            st.session_state.last_updated_id = None
            storage.set_item("parallel_counters", [])
            st.success("すべて削除しました")
            st.rerun()

    st.write("---")
    st.info("各カードの数値をクリックして直接入力することはできませんが、ボタン操作で素早くカウントできます。")

render_donation_box("https://qr.paypay.ne.jp/p2p01_jsHjvMAenqfvI10s", is_sidebar=True)
