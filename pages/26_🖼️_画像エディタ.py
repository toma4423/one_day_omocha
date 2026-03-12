import base64
from io import BytesIO

import streamlit as st
from PIL import Image

from src.utils.image_editor import ImageProcessParams, load_image_with_orientation, process_image
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box

# ページ設定
st.set_page_config(page_title="画像エディタ | 今日のおもちゃ箱", page_icon="🖼️", layout="wide")

# ストレージ初期化
storage = SafeStorage()


def main():
    st.title("🖼️ 画像エディタ")
    st.caption("画像の切り抜き、リサイズ、比率変更が簡単に行えます。")

    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 編集設定")

        # アスペクト比プリセット
        ratio_options = {
            "1:1 (正方形)": (1.0, 1.0),
            "16:9 (ワイド)": (16.0, 9.0),
            "9:16 (縦長/TikTok)": (9.0, 16.0),
            "4:3 (標準)": (4.0, 3.0),
            "3:4 (縦長)": (3.0, 4.0),
            "カスタム": (None, None),
        }

        selected_ratio_name = st.selectbox("アスペクト比", list(ratio_options.keys()), index=0)

        if selected_ratio_name == "カスタム":
            col1, col2 = st.columns(2)
            aspect_x = col1.number_input("横比率", value=1.0, min_value=0.1, step=0.1)
            aspect_y = col2.number_input("縦比率", value=1.0, min_value=0.1, step=0.1)
        else:
            aspect_x, aspect_y = ratio_options[selected_ratio_name]

        st.divider()

        # ズームと位置調整
        scale = st.slider("ズーム (拡大率)", 0.5, 5.0, 1.0, 0.1)
        offset_x = st.slider("横位置調整", 0.0, 1.0, 0.5, 0.01)
        offset_y = st.slider("縦位置調整", 0.0, 1.0, 0.5, 0.01)

        st.divider()

        # 出力設定
        target_width = st.number_input("出力横幅 (px)", value=1080, min_value=10, step=10)
        output_format = st.radio("出力形式", ["PNG", "JPEG"], horizontal=True)

        render_donation_box(is_sidebar=True)

    # メインエリア
    uploaded_file = st.file_uploader("画像をアップロード (PNG, JPG, WebP)", type=["png", "jpg", "jpeg", "webp"])

    # 永続化された画像の読み込み
    stored_image_data = storage.get_data("image_editor_data")

    if uploaded_file is not None:
        # 新しいファイルがアップロードされた場合
        image_bytes = uploaded_file.getvalue()
        # Storageに保存 (base64)
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        storage.set_data("image_editor_data", encoded)
    elif stored_image_data:
        # Storageから復元
        image_bytes = base64.b64decode(stored_image_data)
    else:
        st.info("画像をアップロードして開始してください。")
        return

    try:
        # 画像の読み込み (EXIF補正あり)
        original_img = load_image_with_orientation(image_bytes)

        # パラメータの作成
        params = ImageProcessParams(
            aspect_ratio_x=aspect_x,
            aspect_ratio_y=aspect_y,
            scale=scale,
            offset_x=offset_x,
            offset_y=offset_y,
            target_width=target_width,
            output_format=output_format,
        )

        # 画像処理
        processed_image_bytes = process_image(original_img, params)

        # プレビューとダウンロード
        col_prev, col_info = st.columns([2, 1])

        with col_prev:
            st.subheader("👁️ プレビュー")
            st.image(processed_image_bytes, use_container_width=True)

        with col_info:
            st.subheader("📄 情報")
            processed_img_pil = Image.open(BytesIO(processed_image_bytes))
            st.write(f"サイズ: {processed_img_pil.width} x {processed_img_pil.height} px")
            st.write(f"形式: {output_format}")

            # ダウンロードボタン
            ext = output_format.lower()
            st.download_button(
                label="📥 加工後の画像をダウンロード",
                data=processed_image_bytes,
                file_name=f"edited_image.{ext}",
                mime=f"image/{ext}",
                use_container_width=True,
                type="primary",
            )

            if st.button("🗑️ 画像をクリア", use_container_width=True):
                storage.clear_data("image_editor_data")
                st.rerun()

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        if st.button("設定をリセット"):
            storage.clear_data("image_editor_data")
            st.rerun()


if __name__ == "__main__":
    main()
