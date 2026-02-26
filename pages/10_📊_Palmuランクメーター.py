import json
from datetime import timedelta

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.image_maker import create_palmu_schedule_image
from src.utils.palmu import (
    calculate_total_points,
    evaluate_rank_status,
    generate_point_presets,
    points_needed_for_keep,
    points_needed_for_rank_up,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box, render_result_box
from src.utils.time import get_jst_now

st.set_page_config(page_title="Palmuランクメーター", page_icon="📊", layout="wide")

storage = SafeStorage(LocalStorage())
PALMU_STORAGE_KEY = "palmu_data"

MAX_DAYS = 14

if "palmu_reset_counter" not in st.session_state:
    st.session_state.palmu_reset_counter = 0

if "palmu_skip_cards" not in st.session_state:
    st.session_state.palmu_skip_cards = 0


def save_to_storage():
    data = {f"day_{i}": st.session_state.get(f"palmu_day_{i}", 1) for i in range(1, MAX_DAYS + 1)}
    data["skip_cards"] = st.session_state.get("palmu_skip_cards", 0)
    storage.set_item(PALMU_STORAGE_KEY, data)


def load_from_storage():
    data = storage.get_item(PALMU_STORAGE_KEY, is_json=True)
    if data:
        for i in range(1, MAX_DAYS + 1):
            val = data.get(f"day_{i}", 1)
            st.session_state[f"palmu_day_{i}"] = 1 if val == 0 else val
        st.session_state.palmu_skip_cards = data.get("skip_cards", 0)
        return True
    return False


def init_palmu_state():
    if "palmu_day_1" not in st.session_state:
        if not load_from_storage():
            for i in range(1, MAX_DAYS + 1):
                st.session_state[f"palmu_day_{i}"] = 1
            st.session_state.palmu_skip_cards = 0


init_palmu_state()

st.title("📊 Palmu週間予定表 (ランクメーター)")
st.markdown(
    "Palmuのデイリーランクポイントを入力して、ランク状況をシミュレーションし、配信用のスケジュール画像を作成します。"
)

# --- サイドバー：セーブ＆ロード ---
with st.sidebar:
    st.header("💾 セーブ & ロード")

    current_data = {f"day_{i}": st.session_state[f"palmu_day_{i}"] for i in range(1, MAX_DAYS + 1)}
    current_data["skip_cards"] = st.session_state.palmu_skip_cards
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
                for i in range(1, MAX_DAYS + 1):
                    st.session_state[f"palmu_day_{i}"] = data_load.get(f"day_{i}", 0)
                st.session_state.palmu_skip_cards = data_load.get("skip_cards", 0)
                save_to_storage()
                st.success("復元しました！")
                st.rerun()
            except Exception:
                st.error("JSONの読み込みに失敗しました")

    st.write("---")
    if st.button("全ての入力をリセット", use_container_width=True):
        for i in range(1, MAX_DAYS + 1):
            st.session_state[f"palmu_day_{i}"] = 1
        st.session_state.palmu_skip_cards = 0
        st.session_state.palmu_reset_counter += 1
        storage.delete_item(PALMU_STORAGE_KEY)
        st.rerun()

# --- 共通設定（開始日と目標・スキップカード） ---
now = get_jst_now()
st.subheader("📅 スケジュール基本設定")
col_date, col_target, col_skip = st.columns(3)

with col_date:
    start_date = st.date_input("開始日", value=now.date())

with col_target:
    target_goal = st.selectbox("目標", options=["ランクアップ (+18pt)", "ランクキープ (+12pt)"])
    target_val = 18 if "アップ" in target_goal else 12

with col_skip:
    st.session_state.palmu_skip_cards = st.number_input(
        "スキップカード使用枚数",
        min_value=0,
        max_value=3,
        value=st.session_state.palmu_skip_cards,
        on_change=save_to_storage,
    )

total_days = 7 + st.session_state.palmu_skip_cards

st.write("---")

# --- おすすめプリセット ---
with st.expander("💡 おすすめのポイント取得パターンを見る（クリックで展開）"):
    st.markdown("目標を達成するための効率的なポイントの取り方の例です。ボタンを押すと下に反映されます。")
    presets = generate_point_presets(target_val)

    cols_preset = st.columns(len(presets))
    for idx, (p, col) in enumerate(zip(presets, cols_preset, strict=False)):
        with col:
            st.markdown(f"**パターン {idx + 1}**")
            st.markdown(f"合計: **{sum(p)} pt**")
            p_str = " / ".join([f"+{x}" if x > 0 else "0" for x in p])
            st.caption(f"[{p_str}]")

            if st.button("適用", key=f"apply_preset_{target_val}_{idx}"):
                # 適用時、先頭から順にプリセットを入れ、残りのスキップ分を末尾に「スキップ」として設定
                for i in range(1, MAX_DAYS + 1):
                    if i <= 7:
                        st.session_state[f"palmu_day_{i}"] = p[i - 1]
                    elif i <= total_days:
                        st.session_state[f"palmu_day_{i}"] = "スキップ"
                    else:
                        st.session_state[f"palmu_day_{i}"] = 0
                save_to_storage()
                st.rerun()

st.write("---")

# --- メインエリア ---
point_options = ["スキップ", 1, 2, 4, 6]
weekdays = ["月", "火", "水", "木", "金", "土", "日"]

col_input, col_space, col_result = st.columns([2, 0.5, 2])
reset_id = st.session_state.palmu_reset_counter

with col_input:
    st.subheader(f"📝 デイリーポイント入力 ({total_days}日間)")
    for i in range(1, total_days + 1):
        current_date = start_date + timedelta(days=i - 1)
        date_label = f"{current_date.month}/{current_date.day} ({weekdays[current_date.weekday()]})"

        val = st.session_state.get(f"palmu_day_{i}", 1)
        # 以前のバージョンで保存された0が読み込まれた場合、1に変換する
        if val == 0:
            val = 1
            st.session_state[f"palmu_day_{i}"] = val

        index = point_options.index(val) if val in point_options else 1  # デフォルトは1

        st.session_state[f"palmu_day_{i}"] = st.selectbox(
            date_label,
            options=point_options,
            index=index,
            key=f"p_day_{i}_{reset_id}",
            on_change=save_to_storage,
            format_func=lambda x: (
                f"+{x} pt" if isinstance(x, int) and x > 0 else (f"{x} pt" if isinstance(x, int) else str(x))
            ),
        )

with col_result:
    st.subheader("📈 結果")
    daily_points = [st.session_state[f"palmu_day_{i}"] for i in range(1, total_days + 1)]
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

st.write("---")
st.header("🗓️ スケジュール画像生成")
st.markdown("上記で入力したポイント予定をもとに、配信用のスケジュール画像（背景透過）を作成します。")

col_img_settings, col_img_preview = st.columns([1, 1])

with col_img_settings:
    st.subheader("⚙️ 画像設定")

    title_text = st.text_input("タイトル", value=f"{start_date.month}月 スケジュール")

    st.markdown("#### カラー設定")
    col_color1, col_color2 = st.columns(2)
    with col_color1:
        img_text_color = st.color_picker("文字の色", value="#FFFFFF")
    with col_color2:
        img_frame_color = st.color_picker("フレームの色", value="#FF5722")

    is_transparent = st.checkbox("枠内の背景を完全に透過する", value=False)
    if is_transparent:
        img_bg_color_rgba = "#00000000"
    else:
        img_bg_color = st.color_picker("枠内の背景色", value="#000000")
        img_bg_alpha = st.slider("枠内の不透明度 (%)", min_value=0, max_value=100, value=80)
        alpha_hex = f"{int(img_bg_alpha * 255 / 100):02X}"
        img_bg_color_rgba = f"{img_bg_color}{alpha_hex}"

    st.markdown("#### サイズ・形状設定")
    img_frame_width = st.slider("フレームの太さ", min_value=0, max_value=30, value=8)
    img_corner_radius = st.slider("角丸の大きさ", min_value=0, max_value=200, value=30)
    img_width = st.number_input("画像の幅", min_value=300, max_value=1000, value=600, step=10)

with col_img_preview:
    st.subheader("👁️ プレビュー")
    try:
        # スケジュールデータの構築
        schedule_data = []
        for i in range(1, total_days + 1):
            current_date = start_date + timedelta(days=i - 1)
            date_str = f"{current_date.month}/{current_date.day} ({weekdays[current_date.weekday()]})"
            pt = st.session_state[f"palmu_day_{i}"]

            if pt == "スキップ":
                pt_str = "スキップ"
            else:
                pt_str = f"+{pt}pt" if pt > 0 else "0pt"

            schedule_data.append((date_str, pt_str))

        img_bytes = create_palmu_schedule_image(
            title=title_text,
            schedule_data=schedule_data,
            text_color=img_text_color,
            frame_color=img_frame_color,
            bg_color=img_bg_color_rgba,
            frame_width=img_frame_width,
            corner_radius=img_corner_radius,
            width=img_width,
        )

        # 背景透過が分かりやすいようにCSSで市松模様をプレビューの背景に敷く
        st.markdown(
            """
            <style>
            .preview-container {
                background-color: #eee;
                background-image: linear-gradient(45deg, #ccc 25%, transparent 25%, transparent 75%, #ccc 75%, #ccc),
                                  linear-gradient(45deg, #ccc 25%, transparent 25%, transparent 75%, #ccc 75%, #ccc);
                background-size: 20px 20px;
                background-position: 0 0, 10px 10px;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 20px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        import base64

        b64_img = base64.b64encode(img_bytes).decode()
        st.markdown(
            f'<div class="preview-container"><img src="data:image/png;base64,{b64_img}" style="max-width: 100%; height: auto;"></div>',
            unsafe_allow_html=True,
        )

        st.download_button(
            label="画像をダウンロード (PNG)",
            data=img_bytes,
            file_name=f"palmu_schedule_{start_date.strftime('%Y%m%d')}.png",
            mime="image/png",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"画像の生成中にエラーが発生しました: {e}")

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
