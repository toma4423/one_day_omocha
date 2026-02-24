from src.utils.sugoroku import calculate_new_position, init_board_data


def test_sugoroku_linear_move():
    # 10マス、現在地0、出目3 -> 3
    assert calculate_new_position(0, 3, 10, False) == 3
    # 10マス、現在地8、出目1 -> 9 (ゴール)
    assert calculate_new_position(8, 1, 10, False) == 9
    # 10マス、現在地8、出目5 -> 9 (オーバーしてもゴールで止まる)
    assert calculate_new_position(8, 5, 10, False) == 9


def test_sugoroku_loop_move():
    # 10マス、現在地0、出目3 -> 3
    assert calculate_new_position(0, 3, 10, True) == 3
    # 10マス、現在地9、出目1 -> 0 (一周して最初に戻る)
    assert calculate_new_position(9, 1, 10, True) == 0
    # 10マス、現在地9、出目5 -> 4 (一周以上して進む)
    assert calculate_new_position(9, 5, 10, True) == 4
    # ちょうど一周
    assert calculate_new_position(0, 10, 10, True) == 0


def test_init_board_data_linear():
    total_tiles = 5
    board_type = "スタートからゴール"
    data = init_board_data(total_tiles, board_type)
    assert len(data) == 5
    assert data["sg_tile_0"] == "🚩 START"
    assert data["sg_tile_4"] == "🏆 GOAL"
    assert data["sg_tile_2"] == "マス 3"


def test_init_board_data_loop():
    total_tiles = 3
    board_type = "循環型（ループ）"
    data = init_board_data(total_tiles, board_type)
    assert len(data) == 3
    assert data["sg_tile_0"] == "マス 1"
    assert data["sg_tile_1"] == "マス 2"
    assert data["sg_tile_2"] == "マス 3"
