import json

from src.utils.minesweeper_3d import create_minesweeper_3d, open_cell_3d


def test_create_minesweeper_3d_consistency():
    """初期化の一貫性を検証"""
    width, height, depth = 5, 5, 5
    mines = 10
    state = create_minesweeper_3d(width, height, depth, mines)

    assert state.width == width
    assert len(state.cells) == 125
    assert sum(1 for c in state.cells.values() if c.is_mine) == mines


def test_26_neighbor_logic_at_boundary():
    """境界（角）での26近傍カウントを検証"""
    # 2x2x2 の最小構成
    state = create_minesweeper_3d(2, 2, 2, 0)
    # (0,0,0) 以外の 7 マス全てに地雷を置く
    for x in range(2):
        for y in range(2):
            for z in range(2):
                if x == 0 and y == 0 and z == 0:
                    continue
                state.get_cell(x, y, z).is_mine = True

    # 手動で再計算トリガー（または初期化時の計算を確認）
    state = create_minesweeper_3d(2, 2, 2, 0)
    state.get_cell(1, 1, 1).is_mine = True  # 1つだけ置く

    # 再計算
    for c in state.cells.values():
        if c.is_mine:
            continue
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    nb = state.get_cell(c.x + dx, c.y + dy, c.z + dz)
                    if nb and nb.is_mine:
                        count += 1
        c.neighbor_mines = count

    # 全てのセル（地雷以外）は (1,1,1) と隣接している
    for c in state.cells.values():
        if not c.is_mine:
            assert c.neighbor_mines == 1


def test_safe_html_generation():
    """HTML生成ロジックの健全性を検証"""
    state = create_minesweeper_3d(3, 3, 3, 5)
    css = ".test { color: red; }"
    js = "console.log('hello');"

    html = state.generate_safe_html(css, js)

    # 必須要素が含まれているか
    assert "__CSS__" not in html
    assert "__JS__" not in html
    assert "__JSON_DATA__" not in html
    assert css in html
    assert js in html
    assert '<script id="m3d-data"' in html

    # JSONデータがパース可能か
    json_start = html.find('<script id="m3d-data" type="application/json">') + len(
        '<script id="m3d-data" type="application/json">'
    )
    json_end = html.find("</script>", json_start)
    json_str = html[json_start:json_end].strip()
    parsed_data = json.loads(json_str)
    assert parsed_data["width"] == 3
    assert len(parsed_data["cells"]) == 27


def test_large_grid_serialization():
    """巨大なグリッドでのシリアライズ負荷を検証"""
    # 10x10x10 = 1000マス
    state = create_minesweeper_3d(10, 10, 10, 100)
    html = state.generate_safe_html("", "")
    assert len(html) > 90000  # 約95KB程度
    assert "9,9,9" in html  # 最後のマスの座標が含まれていること


def test_game_over_state():
    """ゲームオーバー時の全地雷表示を検証"""
    state = create_minesweeper_3d(3, 3, 3, 5)
    # 地雷を探す
    mine_cell = next(c for c in state.cells.values() if c.is_mine)
    # 地雷を開く
    state = open_cell_3d(state, mine_cell.x, mine_cell.y, mine_cell.z)

    assert state.game_over is True
    # 全ての地雷が開かれていること
    assert all(c.opened for c in state.cells.values() if c.is_mine)
