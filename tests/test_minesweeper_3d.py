import base64

from src.utils.minesweeper_3d import create_minesweeper_3d


def test_base64_data_uri_format():
    """生成されたBase64 Data URIの形式を検証"""
    state = create_minesweeper_3d(2, 2, 2, 1)
    uri = state.generate_base64_html("css", "js")

    # 1. 戻り値が確実に文字列であること
    assert isinstance(uri, str)

    # 2. Data URI 形式であること
    assert uri.startswith("data:text/html;base64,")

    # 3. Base64 デコード -> HTML パースが可能か
    b64_part = uri.split(",")[1]
    html = base64.b64decode(b64_part).decode("utf-8")
    assert "<!DOCTYPE html>" in html
    assert '<script id="m3d-data" type="application/json">' in html


def test_compact_data_types_strict():
    """JSに渡すデータの型が厳密に基本型であることを検証"""
    state = create_minesweeper_3d(3, 3, 3, 5)
    data = state.to_compact_data(ix=1, iy=2, iz=0)

    assert type(data["w"]) is int
    assert data["sel"] == [1, 2, 0]
    assert type(data["c"]) is list


def test_data_uri_size_optimization():
    """10x10x10の巨大データでもData URIが妥当なサイズか検証"""
    state = create_minesweeper_3d(10, 10, 10, 50)
    uri = state.generate_base64_html("", "")

    # Base64は元のサイズの約1.33倍になる
    # 以前の調査でJSONが約10KBだったので、URI全体でも 20KB 程度に収まるはず
    assert len(uri) < 30000
    print(f"Data URI length: {len(uri)} chars")
