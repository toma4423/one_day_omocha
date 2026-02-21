import pytest
from src.utils.sugoroku import calculate_new_position

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
