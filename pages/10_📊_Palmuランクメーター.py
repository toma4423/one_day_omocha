import json

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.palmu import (
    calculate_total_points,
    evaluate_rank_status,
    points_needed_for_keep,
    points_needed_for_rank_up,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_result_box
from src.utils.time import get_jst_now

st.set_page_config(page_title="Palmuランクメーター", page_icon="📊")

storage = SafeStorage(LocalStorage())
PALMU_STORAGE_KEY = "palmu_data"

if "palmu_reset_counter" not in st.session_state:
    st.session_state.palmu_reset_counter = 0


def save_to_storage():
    """現在の状態を LocalStorage に保存します。"""
    data = {f"day_{i}": st.session_state.get(f"palmu_day_{i}", 0) for i in range(1, 8)}
    storage.set_item(PALMU_STORAGE_KEY, data)


def load_from_storage():
    """LocalStorage から状態を復元します。"""
    data = storage.get_item(PALMU_STORAGE_KEY, is_json=True)
    if data:
        for i in range(1, 8):
            st.session_state[f"palmu_day_{i}"] = data.get(f"day_{i}", 0)
        return True
    return False


def init_palmu_state():
    if "palmu_day_1" not in st.session_state:
        if not load_from_storage():
            for i in range(1, 8):
                st.session_state[f"palmu_day_{i}"] = 0


init_palmu_state()

st.title("📊 Palmuランクメーター")
st.markdown("Palmuのデイリーランクポイントを入力して、ランク状況をシミュレーションします。")

# --- サイドバー：セーブ＆ロード ---
with st.sidebar:
    st.header("💾 セーブ & ロード")

    current_data = {f"day_{i}": st.session_state[f"palmu_day_{i}"] for i in range(1, 8)}
    json_str = json.dumps(current_data, indent=2)
    timestamp = get_jst_now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="JSONをダウンロード",
        data=json_str,
        file_name=f"palmu_rank_{timestamp}.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_file = st.file_uploader("JSONをアップロード", type="json")
    if uploaded_file is not None:
        if st.button("復元する", use_container_width=True):
            try:
                data_load = json.load(uploaded_file)
                for i in range(1, 8):
                    st.session_state[f"palmu_day_{i}"] = data_load.get(f"day_{i}", 0)
                save_to_storage()
                st.success("復元しました！")
                st.rerun()
            except Exception:
                st.error("JSONの読み込みに失敗しました")

    st.write("---")
    if st.button("全ての入力をリセット", use_container_width=True):
        for i in range(1, 8):
            st.session_state[f"palmu_day_{i}"] = 0
        st.session_state.palmu_reset_counter += 1
        storage.delete_item(PALMU_STORAGE_KEY)
        st.rerun()

# --- メインエリア ---
point_options = [0, 1, 2, 4, 6]

col_input, col_space, col_result = st.columns([2, 0.5, 2])
reset_id = st.session_state.palmu_reset_counter

with col_input:
    st.subheader("📝 デイリーポイント入力")
    for i in range(1, 8):
        val = st.session_state[f"palmu_day_{i}"]
        index = point_options.index(val) if val in point_options else 0
        st.session_state[f"palmu_day_{i}"] = st.selectbox(
            f"{i}日目",
            options=point_options,
            index=index,
            key=f"p_day_{i}_{reset_id}",
            on_change=save_to_storage,
            format_func=lambda x: f"+{x} pt" if x > 0 else "0 pt",
        )

with col_result:
    st.subheader("📈 結果")
    daily_points = [st.session_state[f"palmu_day_{i}"] for i in range(1, 8)]
    total = calculate_total_points(daily_points)
    status = evaluate_rank_status(total)

    if status == "ランクアップ":
        status_color = "#E8F5E9"
        border_color = "#2E7D32"
        text_color = "#2E7D32"
    elif status == "キープ":
        status_color = "#FFF3E0"
        border_color = "#F57C00"
        text_color = "#E65100"
    else:
        status_color = "#FFEBEE"
        border_color = "#C62828"
        text_color = "#C62828"

    render_result_box(
        "現在の状態",
        status,
        bg_color=status_color,
        border_color=border_color,
        text_color=text_color,
        font_size=40,
    )

    st.metric("合計ポイント", f"{total} pt")

    if status != "ランクアップ":
        st.write("---")
        st.markdown("#### あと必要なポイント")
        if status == "ランクダウン":
            keep_need = points_needed_for_keep(total)
            st.info(f"🛡️ キープまで: あと **{keep_need}** pt")

        up_need = points_needed_for_rank_up(total)
        st.success(f"🚀 ランクアップまで: あと **{up_need}** pt")
    else:
        st.write("---")
        st.success("🎉 ランクアップ確実です！おめでとうございます！")

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
