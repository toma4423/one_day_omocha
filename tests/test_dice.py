import pytest
from src.utils.dice import evaluate_hand

def test_evaluate_hand_pinzoro():
    # ピンゾロ (1-1-1)
    assert evaluate_hand([1, 1, 1]) == "PINZORO"

def test_evaluate_hand_arashi():
    # アラシ (6-6-6)
    assert evaluate_hand([6, 6, 6]) == "ARASHI_6"
    # アラシ (2-2-2)
    assert evaluate_hand([2, 2, 2]) == "ARASHI_2"

def test_evaluate_hand_shigoro():
    # シゴロ (4-5-6)
    assert evaluate_hand([4, 5, 6]) == "SHIGORO"
    # ソートされていなくても判定できること
    assert evaluate_hand([6, 4, 5]) == "SHIGORO"

def test_evaluate_hand_hifumi():
    # ヒフミ (1-2-3)
    assert evaluate_hand([1, 2, 3]) == "HIFUMI"
    assert evaluate_hand([3, 1, 2]) == "HIFUMI"

def test_evaluate_hand_point():
    # 6の目 (2-2-6)
    assert evaluate_hand([2, 2, 6]) == "POINT_6"
    # 1の目 (5-1-5)
    assert evaluate_hand([5, 1, 5]) == "POINT_1"
    # 2の目 (2-4-4)
    assert evaluate_hand([2, 4, 4]) == "POINT_2"

def test_evaluate_hand_buta():
    # ブタ (役なし)
    assert evaluate_hand([1, 2, 4]) == "BUTA"
    assert evaluate_hand([1, 4, 6]) == "BUTA"
    assert evaluate_hand([2, 3, 5]) == "BUTA"

def test_evaluate_hand_invalid():
    # 無効な入力 (要素数不足など)
    assert evaluate_hand([1, 1]) == "BUTA"
    assert evaluate_hand([1, 2, 3, 4]) == "BUTA"
