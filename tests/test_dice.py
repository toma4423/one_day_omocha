from src.utils.dice import evaluate_hand, roll_dice


def test_roll_dice():
    results = roll_dice(3, 6)
    assert len(results) == 3
    for r in results:
        assert 1 <= r <= 6
    
    # Check different parameters
    results = roll_dice(10, 100)
    assert len(results) == 10
    for r in results:
        assert 1 <= r <= 100

def test_evaluate_hand_pinzoro():
    # ピンゾロ (1-1-1)
    assert evaluate_hand([1, 1, 1]) == "PINZORO"

def test_evaluate_hand_arashi():
    # 全てのアラシをテスト (1はPINZOROになるはず)
    assert evaluate_hand([1, 1, 1]) == "PINZORO"
    assert evaluate_hand([2, 2, 2]) == "ARASHI_2"
    assert evaluate_hand([3, 3, 3]) == "ARASHI_3"
    assert evaluate_hand([4, 4, 4]) == "ARASHI_4"
    assert evaluate_hand([5, 5, 5]) == "ARASHI_5"
    assert evaluate_hand([6, 6, 6]) == "ARASHI_6"

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
    # 全てのポイントをテスト
    assert evaluate_hand([2, 2, 1]) == "POINT_1"
    assert evaluate_hand([5, 5, 2]) == "POINT_2"
    assert evaluate_hand([1, 1, 3]) == "POINT_3"
    assert evaluate_hand([6, 6, 4]) == "POINT_4"
    assert evaluate_hand([4, 4, 5]) == "POINT_5"
    assert evaluate_hand([3, 3, 6]) == "POINT_6"
    
    # 異なる並び順
    assert evaluate_hand([2, 1, 2]) == "POINT_1"
    assert evaluate_hand([2, 2, 6]) == "POINT_6"
    assert evaluate_hand([6, 2, 2]) == "POINT_6"

def test_evaluate_hand_buta():
    # ブタ (役なし)
    assert evaluate_hand([1, 2, 4]) == "BUTA"
    assert evaluate_hand([1, 4, 6]) == "BUTA"
    assert evaluate_hand([2, 3, 5]) == "BUTA"
    # リーチっぽくてもブタ
    assert evaluate_hand([1, 2, 4]) == "BUTA"

def test_evaluate_hand_invalid():
    # 無効な入力 (要素数不足など)
    assert evaluate_hand([1, 1]) == "BUTA"
    assert evaluate_hand([1, 2, 3, 4]) == "BUTA"
    assert evaluate_hand([]) == "BUTA"
