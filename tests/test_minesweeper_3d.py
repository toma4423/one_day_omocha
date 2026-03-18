import json

from src.utils.minesweeper_3d import create_minesweeper_3d, open_cell_3d


def test_cell_list_structure():
    """リスト形式への移行が正しいか検証"""
    state = create_minesweeper_3d(3, 3, 3, 5)
    assert hasattr(state, "cell_list")
    assert len(state.cell_list) == 27
    assert isinstance(state.cell_list[0].x, int)


def test_html_string_type_and_content():
    """TypeErrorを防止するための戻り値チェック"""
    state = create_minesweeper_3d(2, 2, 2, 2)
    css = "body { background: black; }"
    js = "console.log('test');"

    # メソッドとして呼び出す
    html = state.generate_safe_html(css, js)

    # 1. 戻り値が確実に文字列であること
    assert isinstance(html, str)

    # 2. テンプレート置換が正しく行われているか
    assert css in html
    assert js in html
    assert '<script id="m3d-data" type="application/json">' in html

    # 3. JSONが隔離されており、パース可能か
    json_part = html.split('<script id="m3d-data" type="application/json">')[1].split("</script>")[0]
    data = json.loads(json_part)
    assert data["width"] == 2
    assert len(data["cell_list"]) == 8


def test_recursive_open_with_list():
    """リスト形式での再帰オープンが正しく動作するか検証"""
    # 3x3x3 地雷なし
    state = create_minesweeper_3d(3, 3, 3, 0)
    # 中央を開く
    state = open_cell_3d(state, 1, 1, 1)

    # 全てのセルが開かれていること
    assert all(c.opened for c in state.cell_list)


def test_large_grid_safety():
    """巨大なグリッドでもシリアライズが安全に行えるか検証"""
    # 10x10x10 = 1000マス
    state = create_minesweeper_3d(10, 10, 10, 50)
    html = state.generate_safe_html("", "")

    assert isinstance(html, str)
    assert len(html) > 50000  # 適切なデータ量
    assert "cell_list" in html
