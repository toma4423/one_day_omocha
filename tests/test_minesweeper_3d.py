import base64
import json

from src.utils.minesweeper_3d import create_minesweeper_3d


def test_base64_html_generation():
    """Base64方式のHTML生成が正しく行われ、TypeErrorの原因を排除できているか検証"""
    state = create_minesweeper_3d(3, 3, 3, 5)
    css = "body { margin: 0; }"
    js = "console.log('test');"

    html = state.generate_safe_html(css, js)

    # 1. 戻り値が確実に文字列であること
    assert isinstance(html, str)

    # 2. Base64データが埋め込まれているか
    assert '<script id="m3d-data-b64" type="text/plain">' in html

    # 3. データのデコード検証
    # 文字列からBase64部分を抽出
    marker = '<script id="m3d-data-b64" type="text/plain">'
    start = html.find(marker) + len(marker)
    end = html.find("</script>", start)
    b64_str = html[start:end].strip()

    # Base64デコード -> JSONパース
    decoded_json = base64.b64decode(b64_str).decode("utf-8")
    data = json.loads(decoded_json)

    assert data["width"] == 3
    assert len(data["cell_list"]) == 27
    assert "game_over" in data


def test_html_safety_no_fstrings():
    """HTML内に波括弧が含まれていてもパースエラーにならない構造か検証"""
    state = create_minesweeper_3d(2, 2, 2, 1)
    # JS/CSS内に波括弧を多用
    css = ".test { content: '{edge_case}'; }"
    js = "if(true) { const x = { a: 1 }; }"

    html = state.generate_safe_html(css, js)
    assert isinstance(html, str)
    assert css in html
    assert js in html


def test_large_data_robustness():
    """10x10x10の巨大データでもBase64化が正常に行われるか"""
    state = create_minesweeper_3d(10, 10, 10, 100)
    html = state.generate_safe_html("", "")
    assert len(html) > 100000
    assert "m3d-data-b64" in html
