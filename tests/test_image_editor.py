import io

import pytest
from PIL import Image
from pydantic import ValidationError

from src.utils.image_editor import ImageProcessParams, load_image_with_orientation, process_image


def test_process_image_square():
    # 200x100 の画像を作成 (赤い横長画像)
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


def test_process_image_9_16():
    # 100x100 の画像を作成
    img = Image.new("RGBA", (100, 100), (0, 255, 0, 255))
    params = ImageProcessParams(
        aspect_ratio_x=9, aspect_ratio_y=16, scale=1.0, offset_x=0.5, offset_y=0.5, target_width=90, output_format="PNG"
    )

    result_bytes = process_image(img, params)
    result_img = Image.open(io.BytesIO(result_bytes))

    # target_width=90 なので高さは 90 * (16/9) = 160
    assert result_img.size == (90, 160)


def test_process_image_zoom():
    # 100x100 の画像を作成、中央に小さな青い四角
    img = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    img.putpixel((50, 50), (0, 0, 255, 255))

    # ズームなし
    params_no_zoom = ImageProcessParams(scale=1.0, target_width=100)
    res_no_zoom = Image.open(io.BytesIO(process_image(img, params_no_zoom)))

    # ズームあり (2倍) -> 中央が拡大される
    params_zoom = ImageProcessParams(scale=2.0, target_width=100)
    res_zoom = Image.open(io.BytesIO(process_image(img, params_zoom)))

    assert res_no_zoom.size == (100, 100)
    assert res_zoom.size == (100, 100)
    # ズームすると中央のピクセルが大きくなるはず


def test_process_image_jpeg_output():
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    params = ImageProcessParams(output_format="JPEG", target_width=50)

    result_bytes = process_image(img, params)
    # JPEGはアルファチャンネルを持たないので RGB として読み込めるはず
    result_img = Image.open(io.BytesIO(result_bytes))
    assert result_img.format == "JPEG"
    assert result_img.mode == "RGB"


def test_invalid_params():
    # 負のスケールや0のアスペクト比は Pydantic でエラーになるべき
    with pytest.raises(ValidationError):
        ImageProcessParams(scale=0)

    with pytest.raises(ValidationError):
        ImageProcessParams(aspect_ratio_x=-1)


def test_load_image_with_orientation():
    # PNG画像を作成
    img = Image.new("RGBA", (10, 20), (0, 0, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    loaded_img = load_image_with_orientation(buf.getvalue())
    assert loaded_img.size == (10, 20)
    assert loaded_img.mode == "RGBA"
