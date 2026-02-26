import json
from datetime import timedelta

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.image_maker import create_palmu_calendar_grid_image
from src.utils.palmu import (
    calculate_total_points,
    evaluate_rank_status,
    points_needed_for_rank_up,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box
from src.utils.time import get_jst_now

st.set_page_config(page_title="Palmu月間予定表", page_icon="📅", layout="wide")

storage = SafeStorage(LocalStorage())
PALMU_MONTH_STORAGE_KEY = "palmu_month_data"

# 月間用なので最大31日間を管理
MAX_MONTH_DAYS = 31

if "palmu_month_reset_counter" not in st.session_state:
    st.session_state.palmu_month_reset_counter = 0

if "palmu_month_skip_cards" not in st.session_state:
    st.session_state.palmu_month_skip_cards = 0


def save_to_storage():
    data = {f"day_{i}": st.session_state.get(f"pm_day_{i}", 1) for i in range(1, MAX_MONTH_DAYS + 1)}
    data["skip_cards"] = st.session_state.get("palmu_month_skip_cards", 0)
    storage.set_item(PALMU_MONTH_STORAGE_KEY, data)


def load_from_storage():
    data = storage.get_item(PALMU_MONTH_STORAGE_KEY, is_json=True)
    if data:
        for i in range(1, MAX_MONTH_DAYS + 1):
            val = data.get(f"day_{i}", 1)
            st.session_state[f"pm_day_{i}"] = 1 if val == 0 else val
        st.session_state.palmu_month_skip_cards = data.get("skip_cards", 0)
        return True
    return False


def init_palmu_month_state():
    if "pm_day_1" not in st.session_state:
        if not load_from_storage():
            for i in range(1, MAX_MONTH_DAYS + 1):
                st.session_state[f"pm_day_{i}"] = 1
            st.session_state.palmu_month_skip_cards = 0


init_palmu_month_state()

st.title("📅 Palmu月間予定表")
st.markdown("1ヶ月間のランクポイント予定を管理し、配信用のスケジュール画像を作成します。")

# --- サイドバー：セーブ＆ロード ---
with st.sidebar:
    st.header("💾 セーブ & ロード")

    current_data = {f"day_{i}": st.session_state[f"pm_day_{i}"] for i in range(1, MAX_MONTH_DAYS + 1)}
    current_data["skip_cards"] = st.session_state.palmu_month_skip_cards
    json_str = json.dumps(current_data, indent=2)
    timestamp = get_jst_now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="JSONをダウンロード",
        data=json_str,
        file_name=f"palmu_month_{timestamp}.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_file = st.file_uploader("JSONをアップロード", type="json")
    if uploaded_file is not None:
        if st.button("復元する", use_container_width=True):
            try:
                data_load = json.load(uploaded_file)
                for i in range(1, MAX_MONTH_DAYS + 1):
                    st.session_state[f"pm_day_{i}"] = data_load.get(f"day_{i}", 1)
                st.session_state.palmu_month_skip_cards = data_load.get("skip_cards", 0)
                save_to_storage()
                st.success("復元しました！")
                st.rerun()
            except Exception:
                st.error("JSONの読み込みに失敗しました")

    st.write("---")
    if st.button("全ての入力をリセット", use_container_width=True):
        for i in range(1, MAX_MONTH_DAYS + 1):
            st.session_state[f"pm_day_{i}"] = 1
        st.session_state.palmu_month_skip_cards = 0
        st.session_state.palmu_month_reset_counter += 1
        storage.delete_item(PALMU_MONTH_STORAGE_KEY)
        st.rerun()

# --- 基本設定 ---
now = get_jst_now()
st.subheader("📅 スケジュール設定")
col_date, col_days = st.columns(2)

with col_date:
    start_date = st.date_input("開始日", value=now.date())

with col_days:
    # 月間なので28〜31日を選択可能にする（デフォルト31）
    num_days = st.number_input("表示日数", min_value=7, max_value=MAX_MONTH_DAYS, value=31)

st.write("---")

# --- メインエリア ---
point_options = ["スキップ", 1, 2, 4, 6]
weekdays = ["月", "火", "水", "木", "金", "土", "日"]

# 月間なのでグリッド表示にする
st.subheader(f"📝 デイリーポイント入力 ({num_days}日間)")
reset_id = st.session_state.palmu_month_reset_counter

# 7列のグリッドでカレンダー風に表示
cols_per_row = 7
for row_idx in range(0, num_days, cols_per_row):
    cols = st.columns(cols_per_row)
    for col_idx, col in enumerate(cols):
        day_idx = row_idx + col_idx + 1
        if day_idx <= num_days:
            with col:
                current_date = start_date + timedelta(days=day_idx - 1)
                date_label = f"{current_date.month}/{current_date.day}({weekdays[current_date.weekday()]})"

                val = st.session_state.get(f"pm_day_{day_idx}", 1)
                if val == 0:
                    val = 1

                try:
                    index = point_options.index(val)
                except ValueError:
                    index = 1  # デフォルト+1

                st.session_state[f"pm_day_{day_idx}"] = st.selectbox(
                    date_label,
                    options=point_options,
                    index=index,
                    key=f"pm_p_day_{day_idx}_{reset_id}",
                    on_change=save_to_storage,
                    format_func=lambda x: f"+{x}" if isinstance(x, int) else str(x),
                )

st.write("---")

# --- 結果表示（直近7日間ごとのステータス） ---
st.header("📈 ランク状況分析")
st.markdown("開始日から7日間ごとのポイント合計と判定を表示します。")

# 7日周期で計算
num_weeks = (num_days + 6) // 7
week_cols = st.columns(min(num_weeks, 4))  # 最大4週分横並び

for w in range(num_weeks):
    with week_cols[w % 4]:
        start_idx = w * 7 + 1
        end_idx = min(start_idx + 6, num_days)

        week_points = [st.session_state[f"pm_day_{i}"] for i in range(start_idx, end_idx + 1)]
        total = calculate_total_points(week_points)
        status = evaluate_rank_status(total)

        st.markdown(f"**第 {w + 1} 週** ({start_idx}〜{end_idx}日目)")

        color = "#2E7D32" if status == "ランクアップ" else ("#E65100" if status == "キープ" else "#C62828")
        st.markdown(f"<h3 style='color:{color}; margin-bottom:0;'>{status}</h3>", unsafe_allow_html=True)
        st.markdown(f"合計: **{total} pt**")

        if status != "ランクアップ":
            up_need = points_needed_for_rank_up(total)
            st.caption(f"あと {up_need}pt でランクアップ")

st.write("---")

# --- 画像生成 ---
st.header("🗓️ 月間スケジュール画像生成")
st.markdown("入力したポイント予定をもとに、配信用のスケジュール画像（背景透過）を作成します。")

col_img_settings, col_img_preview = st.columns([1, 1.5])

with col_img_settings:
    st.subheader("⚙️ 画像設定")
    title_text = st.text_input("タイトル", value=f"{start_date.month}月 スケジュール")

    img_text_color = st.color_picker("文字の色", value="#FFFFFF")
    img_frame_color = st.color_picker("フレームの色", value="#FF5722")

    is_transparent = st.checkbox("枠内の背景を完全に透過する", value=False, key="pm_trans")
    if is_transparent:
        img_bg_color_rgba = "#00000000"
    else:
        img_bg_color = st.color_picker("枠内の背景色", value="#000000", key="pm_bg")
        img_bg_alpha = st.slider("枠内の不透明度 (%)", min_value=0, max_value=100, value=80, key="pm_alpha")
        alpha_hex = f"{int(img_bg_alpha * 255 / 100):02X}"
        img_bg_color_rgba = f"{img_bg_color}{alpha_hex}"

    img_width = st.number_input("画像の幅", min_value=400, max_value=1200, value=800, step=10, key="pm_width")

with col_img_preview:
    st.subheader("👁️ プレビュー")
    try:
        # スケジュールデータの構築
        calendar_data = []
        for i in range(1, num_days + 1):
            current_date = start_date + timedelta(days=i - 1)
            pt = st.session_state[f"pm_day_{i}"]
            pt_str = "スキップ" if pt == "スキップ" else f"+{pt}pt"

            calendar_data.append(
                {"date": str(current_date.day), "day": weekdays[current_date.weekday()], "point": pt_str}
            )

        # 月間用の描画（カレンダー形式）
        img_bytes = create_palmu_calendar_grid_image(
            title=title_text,
            calendar_data=calendar_data,
            text_color=img_text_color,
            frame_color=img_frame_color,
            bg_color=img_bg_color_rgba,
            width=img_width,
        )

        import base64

        b64_img = base64.b64encode(img_bytes).decode()
        st.markdown(
            f'<div style="background-color:#eee; background-image:linear-gradient(45deg, #ccc 25%, transparent 25%, transparent 75%, #ccc 75%, #ccc), linear-gradient(45deg, #ccc 25%, transparent 25%, transparent 75%, #ccc 75%, #ccc); background-size:20px 20px; background-position:0 0, 10px 10px; padding:20px; border-radius:10px; text-align:center;"><img src="data:image/png;base64,{b64_img}" style="max-width:100%; height:auto;"></div>',
            unsafe_allow_html=True,
        )

        st.download_button(
            label="月間スケジュールをダウンロード (PNG)",
            data=img_bytes,
            file_name=f"palmu_monthly_{start_date.strftime('%Y%m')}.png",
            mime="image/png",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"画像生成エラー: {e}")

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
