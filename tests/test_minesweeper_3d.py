from src.utils.minesweeper_3d import create_minesweeper_3d, open_cell_3d, toggle_flag_3d


def test_create_minesweeper_3d():
    width, height, depth = 3, 3, 3
    mines = 5
    state = create_minesweeper_3d(width, height, depth, mines)

    assert state.width == width
    assert state.height == height
    assert state.depth == depth
    assert len(state.cells) == width * height * depth

    mine_count = sum(1 for c in state.cells.values() if c.is_mine)
    assert mine_count == mines


def test_neighbor_mines_count():
    # 2x2x2 の立方体で、(0,0,0)だけに地雷を置く
    width, height, depth = 2, 2, 2
    state = create_minesweeper_3d(width, height, depth, 0)
    state.cells["0,0,0"].is_mine = True

    # 全てのセルの地雷数を再計算
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                cell = state.get_cell(x, y, z)
                if cell.is_mine:
                    continue

                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        for dz in [-1, 0, 1]:
                            if dx == 0 and dy == 0 and dz == 0:
                                continue
                            neighbor = state.get_cell(x + dx, y + dy, z + dz)
                            if neighbor and neighbor.is_mine:
                                count += 1
                cell.neighbor_mines = count

    # (0,0,0) 以外の全てのセルは (0,0,0) と隣接しているため、neighbor_mines は 1 になるはず
    for key, cell in state.cells.items():
        if key == "0,0,0":
            continue
        assert cell.neighbor_mines == 1


def test_open_cell_recursive():
    # 地雷なしの状態で中央を開くと、全セルが開かれるはず
    state = create_minesweeper_3d(3, 3, 3, 0)
    state = open_cell_3d(state, 1, 1, 1)

    assert all(c.opened for c in state.cells.values())


def test_toggle_flag():
    state = create_minesweeper_3d(3, 3, 3, 5)
    state = toggle_flag_3d(state, 0, 0, 0)
    assert state.get_cell(0, 0, 0).flagged is True

    state = toggle_flag_3d(state, 0, 0, 0)
    assert state.get_cell(0, 0, 0).flagged is False
