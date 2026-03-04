from src.utils.minesweeper import MinesweeperState, init_minesweeper_state


def test_minesweeper_initialization():
    state = init_minesweeper_state(10, 8, 10)
    assert state.width == 10
    assert state.height == 8
    count = sum(row.count(-1) for row in state.board)
    assert count == 10


def test_minesweeper_flood_fill():
    # 4x4のボードで中央付近に爆弾がある場合
    state = MinesweeperState(width=4, height=4, num_mines=1)
    # 1 1 1 0
    # 1 -1 1 0
    # 1 1 1 0
    # 0 0 0 0
    state.board = [[1, 1, 1, 0], [1, -1, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0]]
    state.revealed = [[False] * 4 for _ in range(4)]
    state.flags = [[False] * 4 for _ in range(4)]
    state.status = "playing"

    # 端 (3,3) を開く (0なので周囲が開くはず)
    state.reveal_tile(3, 3)
    # 爆弾に隣接する1のタイルまで開かれる
    assert state.revealed[3][3] == True
    assert state.revealed[0][3] == True
    assert state.revealed[1][2] == True
    assert state.revealed[1][1] == False  # 爆弾


def test_minesweeper_win_condition():
    # 4x4, 1爆弾
    state = MinesweeperState(width=4, height=4, num_mines=1)
    state.board = [[0] * 4 for _ in range(4)]
    state.board[3][3] = -1
    state.revealed = [[False] * 4 for _ in range(4)]
    state.flags = [[False] * 4 for _ in range(4)]
    state.status = "playing"

    # 爆弾以外をすべて開く (flood fillで一気に開く)
    state.reveal_tile(0, 0)

    assert state.status == "won"


def test_minesweeper_lost_condition():
    state = MinesweeperState(width=4, height=4, num_mines=1)
    state.board = [[0] * 4 for _ in range(4)]
    state.board[3][3] = -1
    state.revealed = [[False] * 4 for _ in range(4)]
    state.flags = [[False] * 4 for _ in range(4)]
    state.status = "playing"

    state.reveal_tile(3, 3)
    assert state.status == "lost"
    # 爆弾が表示されること
    assert state.revealed[3][3] == True
