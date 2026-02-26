import streamlit as st

from src.utils.image_maker import create_badge_image
from src.utils.styles import render_donation_box
from src.utils.time import get_jst_now

st.set_page_config(page_title="年月画像メーカー", page_icon="🖼️")

st.title("🖼️ 年月画像メーカー")
st.markdown("配信のオーバーレイやプロフィール、サムネイルなどで使える、背景が透過されたバッジ画像を作成します。")

now = get_jst_now()
default_text = f"{now.year}年 {now.month}月"

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("⚙️ 設定")
    text = st.text_input("表示テキスト", value=default_text)

    st.markdown("#### カラー設定")
    col_color1, col_color2 = st.columns(2)
    with col_color1:
        text_color = st.color_picker("文字の色", value="#FFFFFF")
    with col_color2:
        frame_color = st.color_picker("フレームの色", value="#FF5722")

    is_transparent = st.checkbox("枠内の背景を完全に透過する", value=True)
    if is_transparent:
        bg_color_rgba = "#00000000"
    else:
        bg_color = st.color_picker("枠内の背景色", value="#000000")
        bg_alpha = st.slider("枠内の不透明度 (%)", min_value=0, max_value=100, value=80)
        alpha_hex = f"{int(bg_alpha * 255 / 100):02X}"
        bg_color_rgba = f"{bg_color}{alpha_hex}"

    st.markdown("#### サイズ・形状設定")
    font_size = st.slider("文字サイズ", min_value=20, max_value=120, value=60)
    frame_width = st.slider("フレームの太さ", min_value=0, max_value=30, value=8)
    corner_radius = st.slider("角丸の大きさ", min_value=0, max_value=200, value=30)

    col_size1, col_size2 = st.columns(2)
    with col_size1:
        width = st.number_input("画像の幅", min_value=100, max_value=1000, value=400, step=10)
    with col_size2:
        height = st.number_input("画像の高さ", min_value=50, max_value=1000, value=150, step=10)

with col2:
    st.subheader("👁️ プレビュー")
    try:
        img_bytes = create_badge_image(
            text=text,
            text_color=text_color,
            frame_color=frame_color,
            bg_color=bg_color_rgba,
            frame_width=frame_width,
            corner_radius=corner_radius,
            width=width,
            height=height,
            font_size=font_size,
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
            file_name=f"badge_{now.year}{now.month:02d}.png",
            mime="image/png",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"画像の生成中にエラーが発生しました: {e}")

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
