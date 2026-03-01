from io import BytesIO

from PIL import Image

from src.utils.image_maker import (
    composite_images,
    create_badge_image,
    create_palmu_calendar_grid_image,
    create_palmu_schedule_image,
    hex_to_rgba,
)


def test_hex_to_rgba_variants():
    # 6桁
    assert hex_to_rgba("#FFFFFF") == (255, 255, 255, 255)
    # 8桁 (アルファあり)
    assert hex_to_rgba("#FF000080") == (255, 0, 0, 128)
    # 無効な文字列
    assert hex_to_rgba("INVALID") == (0, 0, 0, 0)
    # 記号なし
    assert hex_to_rgba("00FF00") == (0, 255, 0, 255)


def test_create_badge_image_basic():
    img_bytes = create_badge_image("TEST")
    assert img_bytes.startswith(b"\x89PNG")


def test_create_palmu_schedule_image_basic():
    schedule_data = [("2/27", "+6pt"), ("2/28", "SKIP")]
    img_bytes = create_palmu_schedule_image("Week", schedule_data)
    assert img_bytes.startswith(b"\x89PNG")


def test_create_palmu_calendar_grid_image_with_colors():
    calendar_data = [{"date": "1", "day": "月", "point": "+1pt"}]
    # 背景色指定あり
    img_bytes = create_palmu_calendar_grid_image(
        "Month", calendar_data, cell_bg_colors=["#FF000080"]
    )
    assert img_bytes.startswith(b"\x89PNG")


def test_composite_images_anchors():
    # 100x100 赤背景
    bg = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    bg_buf = BytesIO()
    bg.save(bg_buf, format="PNG")
    bg_bytes = bg_buf.getvalue()

    # 10x10 青前景
    fg = Image.new("RGBA", (10, 10), (0, 0, 255, 255))
    fg_buf = BytesIO()
    fg.save(fg_buf, format="PNG")
    fg_bytes = fg_buf.getvalue()

    # 各アンカーでの合成がエラーなく行えるか
    anchors = ["左上", "中央", "右上", "左下", "右下"]
    for a in anchors:
        result = composite_images(bg_bytes, fg_bytes, offset_x=0, offset_y=0, anchor=a)
        assert isinstance(result, bytes)
        assert result.startswith(b"\x89PNG")

    # スケール変更のテスト
    result_scaled = composite_images(bg_bytes, fg_bytes, 0, 0, scale=2.0)
    img_scaled = Image.open(BytesIO(result_scaled))
    assert img_scaled.size == (100, 100) # 背景サイズは維持されること
