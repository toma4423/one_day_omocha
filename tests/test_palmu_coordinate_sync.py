import pytest


def calculate_expected_absolute(bg_w, bg_h, fg_w, fg_h, px, py, scale, anchor):
    """
    Python側のロジックに基づいた「左上基準の絶対座標」を計算します。
    (src/utils/image_maker.py のロジックをシミュレート)
    """
    fw, fh = fg_w * scale, fg_h * scale
    if anchor == "左上":
        return px, py
    elif anchor == "中央":
        return (bg_w - fw) / 2 + px, (bg_h - fh) / 2 + py
    elif anchor == "右上":
        return (bg_w - fw) - px, py
    elif anchor == "左下":
        return px, (bg_h - fh) - py
    elif anchor == "右下":
        return (bg_w - fw) - px, (bg_h - fh) - py
    elif anchor == "中央左":
        return px, (bg_h - fh) / 2 + py
    elif anchor == "中央右":
        return (bg_w - fw) - px, (bg_h - fh) / 2 + py
    elif anchor == "中央上":
        return (bg_w - fw) / 2 + px, py
    elif anchor == "中央下":
        return (bg_w - fw) / 2 + px, (bg_h - fh) - py
    return px, py

def simulate_js_reverse_calculation(bg_w, bg_h, fg_w, fg_h, abs_x, abs_y, scale, anchor):
    """
    JavaScript側で行っている「絶対座標から相対座標への逆算」をシミュレートします。
    """
    fw, fh = fg_w * scale, fg_h * scale
    if anchor == "左上":
        return abs_x, abs_y
    elif anchor == "中央":
        return abs_x - (bg_w - fw) / 2, abs_y - (bg_h - fh) / 2
    elif anchor == "右上":
        return (bg_w - fw) - abs_x, abs_y
    elif anchor == "左下":
        return abs_x, (bg_h - fh) - abs_y
    elif anchor == "右下":
        return (bg_w - fw) - abs_x, (bg_h - fh) - abs_y
    elif anchor == "中央左":
        return abs_x, abs_y - (bg_h - fh) / 2
    elif anchor == "中央右":
        return (bg_w - fw) - abs_x, abs_y - (bg_h - fh) / 2
    elif anchor == "中央上":
        return abs_x - (bg_w - fw) / 2, abs_y
    elif anchor == "中央下":
        return abs_x - (bg_w - fw) / 2, (bg_h - fh) - abs_y
    return abs_x, abs_y

@pytest.mark.parametrize("anchor", [
    "左上", "中央", "右上", "左下", "右下", "中央左", "中央右", "中央上", "中央下"
])
def test_coordinate_sync_consistency(anchor):
    """
    すべてのアンカーポイントにおいて、
    相対座標 -> 絶対座標 (表示) -> 相対座標 (逆算)
    の変換が元に戻ることをテストします。
    """
    bg_w, bg_h = 1920, 1080
    fg_w, fg_h = 600, 800
    px, py = 123, 456
    scale = 0.85
    
    # 1. Python側での絶対位置計算
    abs_x, abs_y = calculate_expected_absolute(bg_w, bg_h, fg_w, fg_h, px, py, scale, anchor)
    
    # 2. JS側での逆算（マウス移動後のシミュレーション）
    final_px, final_py = simulate_js_reverse_calculation(bg_w, bg_h, fg_w, fg_h, abs_x, abs_y, scale, anchor)
    
    # 元の数値に戻るはず
    assert pytest.approx(final_px) == px
    assert pytest.approx(final_py) == py
