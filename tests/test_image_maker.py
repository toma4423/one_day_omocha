from src.utils.image_maker import create_badge_image, hex_to_rgba


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

    # 枠線なしテスト
    img_bytes_no_frame = create_badge_image("No Frame", frame_width=0)
    assert img_bytes_no_frame.startswith(b"\x89PNG")
