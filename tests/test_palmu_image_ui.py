from io import BytesIO

from PIL import Image

from src.utils.image_maker import create_palmu_calendar_grid_image, create_palmu_schedule_image


def test_weekly_schedule_image_size():
    """週間予定表画像のサイズ取得が正しく行えるか検証"""
    title = "Test Title"
    data = [("3/1", "Plan", "+1pt")]
    img_bytes = create_palmu_schedule_image(title, data)

    img = Image.open(BytesIO(img_bytes))
    assert img.width > 0
    assert img.height > 0
    # デフォルト幅は600
    assert img.width == 600


def test_monthly_calendar_image_size():
    """月間予定表画像のサイズ取得が正しく行えるか検証"""
    title = "Test Month"
    data = [{"date": "1", "day": "月", "point": "+1pt"}]
    img_bytes = create_palmu_calendar_grid_image(title, data)

    img = Image.open(BytesIO(img_bytes))
    assert img.width > 0
    assert img.height > 0
    # デフォルト幅は1000
    assert img.width == 1000


def test_coordinate_calculation_logic():
    """座標計算のロジックが破綻していないか（JSに渡す値の算出用）"""
    bg_w, bg_h = 1920, 1080
    fg_w, fg_h = 600, 400
    scale = 1.0
    px, py = 10, 20

    # 中央下基準
    left_cb = (bg_w - fg_w * scale) / 2 + px
    top_cb = (bg_h - fg_h * scale) - py
    assert left_cb == (1920 - 600) / 2 + 10
    assert top_cb == (1080 - 400) - 20

    # 中央左基準
    left_cl = px
    top_cl = (bg_h - fg_h * scale) / 2 + py
    assert left_cl == 10
    assert top_cl == (1080 - 400) / 2 + 20

