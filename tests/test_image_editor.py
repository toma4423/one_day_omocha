import io

from PIL import Image

from src.utils.image_editor import ImageProcessParams, load_image_with_orientation, process_image


def test_process_image_square():
    # 200x100 の画像を作成
    img = Image.new("RGBA", (200, 100), (255, 0, 0, 255))
    params = ImageProcessParams(
        aspect_ratio_x=1.0,
        aspect_ratio_y=1.0,
        scale=1.0,
        offset_x=0.5,
        offset_y=0.5,
        target_width=50,
        output_format="PNG",
    )

    result_bytes = process_image(img, params)
    result_img = Image.open(io.BytesIO(result_bytes))

    assert result_img.size == (50, 50)
    # 元画像が200x100で、1:1のアスペクト比なら、中央の100x100が切り抜かれるはず


def test_process_image_9_16():
    # 100x100 の画像を作成
    img = Image.new("RGBA", (100, 100), (0, 255, 0, 255))
    params = ImageProcessParams(
        aspect_ratio_x=9, aspect_ratio_y=16, scale=1.0, offset_x=0.5, offset_y=0.5, target_width=90, output_format="PNG"
    )

    result_bytes = process_image(img, params)
    result_img = Image.open(io.BytesIO(result_bytes))

    assert result_img.size == (90, 160)


def test_load_image_with_orientation():
    # 最小限のテスト (orientationがない場合はそのまま読み込まれることを確認)
    img = Image.new("RGBA", (10, 20), (0, 0, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    loaded_img = load_image_with_orientation(buf.getvalue())
    assert loaded_img.size == (10, 20)
