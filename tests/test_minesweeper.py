import numpy as np
import pytest

from src.utils.minesweeper import create_board, is_game_won, reveal_tile


def test_create_board_dimensions():
    w, h, mines = 10, 8, 10
    board = create_board(w, h, mines)
    assert board.shape == (h, w)
    assert np.sum(board == -1) == mines


def test_create_board_invalid_mines():
    with pytest.raises(ValueError):
        create_board(5, 5, 25)


def test_create_board_invalid_dimensions():
    with pytest.raises(ValueError):
        create_board(0, 5, 2)


def test_reveal_tile_simple():
    w, h = 3, 3
    # 0 1 -1
    # 0 1  1
    # 0 0  0
    board = np.array([[0, 1, -1], [0, 1, 1], [0, 0, 0]])
    revealed = np.zeros((h, w), dtype=bool)
    flags = np.zeros((h, w), dtype=bool)

    # 0を開くと周囲も開くはず
    new_revealed = reveal_tile(2, 0, w, h, board, revealed, flags)
    # すべての0と、それに隣接する1が開かれるはず
    # この例では、左2列と下の行が全部開く（爆弾以外）
    assert new_revealed[0, 0] == True
    assert new_revealed[0, 1] == True
    assert new_revealed[0, 2] == False  # 爆弾
    assert new_revealed[1, 0] == True
    assert new_revealed[1, 1] == True
    assert new_revealed[1, 2] == True
    assert new_revealed[2, 0] == True
    assert new_revealed[2, 1] == True
    assert new_revealed[2, 2] == True


def test_reveal_tile_with_flag():
    w, h = 3, 3
    board = np.zeros((h, w), dtype=int)
    revealed = np.zeros((h, w), dtype=bool)
    flags = np.zeros((h, w), dtype=bool)
    flags[0, 0] = True

    new_revealed = reveal_tile(0, 0, w, h, board, revealed, flags)
    assert new_revealed[0, 0] == False


def test_is_game_won():
    board = np.array([[0, -1], [1, 1]])
    revealed = np.array([[True, False], [True, True]])
    assert is_game_won(board, revealed) == True

    revealed[0, 0] = False
    assert is_game_won(board, revealed) == False
