from src.utils.image_maker import (
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
        {"date": "3", "day": "水", "point": "スキップ"},
    ]
    img_bytes = create_palmu_calendar_grid_image("2026年 2月 カレンダー", calendar_data)
    assert isinstance(img_bytes, bytes)
    assert img_bytes.startswith(b"\x89PNG")
