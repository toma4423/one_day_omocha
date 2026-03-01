import json
from datetime import timedelta

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.image_maker import composite_images, create_palmu_calendar_grid_image
from src.utils.palmu import (
    calculate_skip_card_balance,
    evaluate_rank_status,
    get_day_period_assignments,
    group_points_by_active_week,
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
            if val == 0:
                val = 1
            elif val == "スキップ":
                val = "SKIP"
            st.session_state[f"pm_day_{i}"] = val
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
                    val = data_load.get(f"day_{i}", 1)
                    if val == "スキップ":
                        val = "SKIP"
                    st.session_state[f"pm_day_{i}"] = val
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
col_date, col_days, col_skip = st.columns(3)

with col_date:
    start_date = st.date_input("開始日", value=now.date())

with col_days:
    # 月間なので28〜31日を選択可能にする（デフォルト31）
    num_days = st.number_input("表示日数", min_value=7, max_value=MAX_MONTH_DAYS, value=31)

with col_skip:
    initial_skip_cards = st.number_input(
        "現在のスキップカード所持枚数", min_value=0, max_value=10, value=st.session_state.palmu_month_skip_cards
    )
    st.session_state.palmu_month_skip_cards = initial_skip_cards

st.write("---")

# --- メインエリア ---
point_options = ["SKIP", 1, 2, 4, 6]
weekdays_sun_start = ["日", "月", "火", "水", "木", "金", "土"]

# 期間ごとの色設定（背景色 - 視認性向上のため少し濃いめに設定）
PERIOD_COLORS = [
    "#E0E0E0",  # 0: SKIP/休み (グレー)
    "#90CAF9",  # 1: 青系
    "#A5D6A7",  # 2: 緑系
    "#FFCC80",  # 3: オレンジ系
    "#CE93D8",  # 4: 紫系
    "#FFF59D",  # 5: 黄色系
]

st.subheader(f"📝 デイリーポイント入力 ({num_days}日間)")
reset_id = st.session_state.palmu_month_reset_counter

# ランク周期の割り当て計算
daily_vals_for_analysis = [st.session_state.get(f"pm_day_{i}", 1) for i in range(1, num_days + 1)]
# 互換性
for i in range(len(daily_vals_for_analysis)):
    if daily_vals_for_analysis[i] == "スキップ":
        daily_vals_for_analysis[i] = "SKIP"

period_assignments = get_day_period_assignments(daily_vals_for_analysis)

# スキップカード残高の事前計算
skip_balances = calculate_skip_card_balance(initial_skip_cards, start_date, num_days, daily_vals_for_analysis)

# 日曜日開始のためのパディング計算
start_weekday_idx = (start_date.weekday() + 1) % 7

# カレンダー表示用のヘッダー
cols_header = st.columns(7)
for idx, day_name in enumerate(weekdays_sun_start):
    color = "#FF1744" if day_name == "日" else ("#2979FF" if day_name == "土" else "inherit")
    cols_header[idx].markdown(
        f"<div style='text-align:center; font-weight:bold; color:{color};'>{day_name}</div>", unsafe_allow_html=True
    )

# 7列のグリッドでカレンダー風に表示
total_slots = num_days + start_weekday_idx
rows = (total_slots + 6) // 7

for r in range(rows):
    cols = st.columns(7)
    for c in range(7):
        slot_idx = r * 7 + c
        day_idx = slot_idx - start_weekday_idx + 1

        with cols[c]:
            if 1 <= day_idx <= num_days:
                current_date = start_date + timedelta(days=day_idx - 1)
                date_label = f"{current_date.month}/{current_date.day}"

                # ランク周期の表示
                p_idx = period_assignments[day_idx - 1]
                p_text = f"第{p_idx}期" if p_idx > 0 else "休み"
                p_color = PERIOD_COLORS[p_idx % len(PERIOD_COLORS)]

                # UI上で色分けを表現 (コンテナの背景色として疑似的に表現)
                st.markdown(
                    f"<div style='background-color:{p_color}; padding:2px; border-radius:5px; font-size:12px; text-align:center; border:1px solid #ddd; margin-bottom:5px;'>{p_text}</div>",
                    unsafe_allow_html=True,
                )

                # スキップカード残高の表示
                balance = skip_balances[day_idx - 1]
                st.caption(f"🎫 {balance}枚")

                val = st.session_state.get(f"pm_day_{day_idx}", 1)
                if val == 0:
                    val = 1
                elif val == "スキップ":
                    val = "SKIP"
                    st.session_state[f"pm_day_{day_idx}"] = val

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
            else:
                # 範囲外は空欄
                st.write("")

st.write("---")

# --- 結果表示（有効な7日間ごとのステータス） ---
st.header("📈 ランク状況分析")
st.markdown("スキップカードを除いた、有効な配信日7日間ごとの判定を表示します。")

daily_points_all = [st.session_state[f"pm_day_{i}"] for i in range(1, num_days + 1)]
active_weeks = group_points_by_active_week(daily_points_all)

if not active_weeks:
    st.info("データがありません。")
else:
    num_active_weeks = len(active_weeks)
    week_cols = st.columns(min(num_active_weeks, 4))

    for w, week_points in enumerate(active_weeks):
        with week_cols[w % 4]:
            total = sum(week_points)
            status = evaluate_rank_status(total)

            st.markdown(f"**有効第 {w + 1} 期** (7日間分)")

            color = "#2E7D32" if status == "ランクアップ" else ("#E65100" if status == "キープ" else "#C62828")
            st.markdown(f"<h3 style='color:{color}; margin-bottom:0;'>{status}</h3>", unsafe_allow_html=True)
            st.markdown(f"合計: **{total} pt**")

            if status != "ランクアップ":
                up_need = points_needed_for_rank_up(total)
                st.caption(f"あと {up_need}pt でランクアップ")

st.write("---")

# --- 画像生成 ---
st.header("🗓️ 月間スケジュール画像生成 & 合成")
st.markdown("ポイント予定をカレンダー画像化し、お好みの背景画像と合成できます。")

col_img_settings, col_img_preview = st.columns([1, 1.5])

with col_img_settings:
    st.subheader("⚙️ 1. カレンダー画像設定")
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

    st.write("---")
    st.subheader("背景画像と合成 (オプション)")
    bg_file = st.file_uploader("背景画像をアップロード (JPG/PNG)", type=["jpg", "jpeg", "png"], key="pm_bg_upload")

    if bg_file:
        # 画像サイズを取得するために一度開く
        from PIL import Image

        bg_img_tmp = Image.open(bg_file)
        bg_w, bg_h = bg_img_tmp.size
        st.caption(f"背景サイズ: {bg_w} x {bg_h} px")

        st.markdown("#### 合成位置・サイズ調整")

        # 位置プリセット
        st.markdown("快速配置:")
        col_pre1, col_pre2, col_pre3 = st.columns(3)
        if col_pre1.button("左上", use_container_width=True, key="pm_pre_tl"):
            st.session_state.pm_x, st.session_state.pm_y = 50, 50
            st.rerun()
        if col_pre2.button("中央", use_container_width=True, key="pm_pre_c"):
            st.session_state.pm_x, st.session_state.pm_y = (bg_w - int(img_width)) // 2, (bg_h - 600) // 2
            st.rerun()
        if col_pre3.button("右下", use_container_width=True, key="pm_pre_br"):
            st.session_state.pm_x, st.session_state.pm_y = bg_w - int(img_width) - 50, bg_h - 600 - 50
            st.rerun()

        col_pos_x, col_pos_y = st.columns(2)
        with col_pos_x:
            pos_x = st.number_input(
                "左右位置 (X)",
                min_value=-2000,
                max_value=bg_w + 2000,
                value=st.session_state.get("pm_x", 50),
                key="pm_x",
            )
        with col_pos_y:
            pos_y = st.number_input(
                "上下位置 (Y)",
                min_value=-2000,
                max_value=bg_h + 2000,
                value=st.session_state.get("pm_y", 50),
                key="pm_y",
            )

        overlay_scale = st.slider("スケール", min_value=0.1, max_value=2.0, value=1.0, step=0.05, key="pm_scale")
    else:
        pos_x, pos_y, overlay_scale = 50, 50, 1.0

with col_img_preview:
    st.subheader("👁️ プレビュー")
    try:
        # スケジュールデータの構築
        calendar_data = []

        # 1. 開始前の空欄パディング
        for i in range(start_weekday_idx):
            calendar_data.append({"date": "", "day": weekdays_sun_start[i], "point": ""})

        # 2. 実際の日付データ
        for i in range(1, num_days + 1):
            current_date = start_date + timedelta(days=i - 1)
            pt = st.session_state[f"pm_day_{i}"]
            pt_str = "SKIP" if pt == "SKIP" else f"+{pt}pt"

            calendar_data.append(
                {
                    "date": str(current_date.day),
                    "day": weekdays_sun_start[(start_weekday_idx + i - 1) % 7],
                    "point": pt_str,
                }
            )

        # カレンダー画像の生成
        fg_bytes = create_palmu_calendar_grid_image(
            title=title_text,
            calendar_data=calendar_data,
            text_color=img_text_color,
            frame_color=img_frame_color,
            bg_color=img_bg_color_rgba,
            width=img_width,
        )

        final_bytes = fg_bytes
        display_img = fg_bytes

        # 背景画像がある場合は合成
        if bg_file:
            bg_bytes = bg_file.getvalue()
            final_bytes = composite_images(
                bg_bytes=bg_bytes,
                fg_bytes=fg_bytes,
                x=pos_x,
                y=pos_y,
                scale=overlay_scale,
            )
            display_img = final_bytes

        import base64

        b64_img = base64.b64encode(display_img).decode()
        st.markdown(
            f'<div style="background-color:#eee; background-image:linear-gradient(45deg, #ccc 25%, transparent 25%, transparent 75%, #ccc 75%, #ccc), linear-gradient(45deg, #ccc 25%, transparent 25%, transparent 75%, #ccc 75%, #ccc); background-size:20px 20px; background-position:0 0, 10px 10px; padding:20px; border-radius:10px; text-align:center;"><img src="data:image/png;base64,{b64_img}" style="max-width:100%; height:auto;"></div>',
            unsafe_allow_html=True,
        )

        st.download_button(
            label="完成した画像をダウンロード (PNG)",
            data=final_bytes,
            file_name=f"palmu_monthly_final_{get_jst_now().strftime('%Y%m%d_%H%M')}.png",
            mime="image/png",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"画像生成エラー: {e}")

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
