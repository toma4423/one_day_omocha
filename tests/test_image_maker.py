from io import BytesIO

from PIL import Image

from src.utils.image_maker import (
    composite_images,
    create_badge_image,
    create_palmu_calendar_grid_image,
    create_palmu_schedule_image,
    hex_to_rgba,
)


def test_hex_to_rgba():
    assert hex_to_rgba("#FFFFFF") == (255, 255, 255, 255)
    assert hex_to_rgba("#FF0000") == (255, 0, 0, 255)
    assert hex_to_rgba("#00000000") == (0, 0, 0, 0)
    assert hex_to_rgba("#80808080") == (128, 128, 128, 128)
    assert hex_to_rgba("INVALID") == (0, 0, 0, 0)


def test_create_badge_image():
    # 生成テスト
    img_bytes = create_badge_image("2026年 2月")
    assert isinstance(img_bytes, bytes)
    assert len(img_bytes) > 0
    assert img_bytes.startswith(b"\x89PNG")


def test_create_palmu_schedule_image():
    schedule_data = [
        ("2/27 (金)", "+2pt"),
        ("2/28 (土)", "+4pt"),
    ]
    img_bytes = create_palmu_schedule_image("スケジュール", schedule_data)
    assert isinstance(img_bytes, bytes)
    assert img_bytes.startswith(b"\x89PNG")


def test_create_palmu_calendar_grid_image():
    calendar_data = [
        {"date": "1", "day": "月", "point": "+4pt"},
        {"date": "2", "day": "火", "point": "+2pt"},
        {"date": "3", "day": "水", "point": "SKIP"},
    ]
    img_bytes = create_palmu_calendar_grid_image("2026年 2月 カレンダー", calendar_data)
    assert isinstance(img_bytes, bytes)
    assert img_bytes.startswith(b"\x89PNG")


def test_composite_images():
    # 100x100 赤背景
    bg = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    bg_buf = BytesIO()
    bg.save(bg_buf, format="PNG")

    # 50x50 青前景
    fg = Image.new("RGBA", (50, 50), (0, 0, 255, 255))
    fg_buf = BytesIO()
    fg.save(fg_buf, format="PNG")

    result_bytes = composite_images(bg_buf.getvalue(), fg_buf.getvalue(), 10, 10, scale=1.0)
    assert isinstance(result_bytes, bytes)
    assert result_bytes.startswith(b"\x89PNG")

    # 結果の画像を確認（青い領域があるか等、簡易的に）
    res_img = Image.open(BytesIO(result_bytes))
    assert res_img.size == (100, 100)
