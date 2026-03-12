from src.utils.sugoroku import calculate_new_position, create_board


def test_calculate_new_position_linear():
    # 直線型：20マス (0-19)
    assert calculate_new_position(0, 3, 20, False) == 3
    assert calculate_new_position(18, 5, 20, False) == 19  # ゴールで止まる


def test_calculate_new_position_loop():
    # 循環型：20マス (0-19)
    assert calculate_new_position(18, 5, 20, True) == 3  # (18+5)%20 = 3


def test_create_board():
    board = create_board(total_tiles=10, is_loop=False)
    assert len(board.tiles) == 10
    assert board.tiles[0].text == "🚩 START"
    assert board.tiles[9].text == "🏆 GOAL"

    board_loop = create_board(total_tiles=10, is_loop=True)
    assert board_loop.tiles[0].text == "マス 1"
