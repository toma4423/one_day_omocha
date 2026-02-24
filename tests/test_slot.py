from src.utils.slot import evaluate_slot_spin, spin_reels


def test_spin_reels():
    symbol_data = [
        {"char": "A", "weight": 1, "image_url": None},
        {"char": "B", "weight": 1, "image_url": "http://example.com/b.png"},
        {"char": "C", "weight": 1, "image_url": None},
    ]
    result = spin_reels(symbol_data, 3)
    assert len(result) == 3
    # 戻り値が辞書のリストであることを確認
    for item in result:
        assert isinstance(item, dict)
        assert "char" in item
        assert "image_url" in item


def test_spin_reels_weighted():
    # 重みが極端な場合
    symbol_data = [
        {"char": "A", "weight": 1000, "image_url": None},
        {"char": "B", "weight": 0, "image_url": None},
    ]
    result = spin_reels(symbol_data, 10)
    for item in result:
        assert item["char"] == "A"


def test_evaluate_slot_spin_exact_match():
    payouts = [
        {"pattern": ["7", "7", "7"], "name": "JACKPOT", "score": 1000},
        {"pattern": ["A", "A", "A"], "name": "AAA", "score": 100},
    ]

    # 成立 (辞書のリストを渡す)
    res = evaluate_slot_spin(
        [{"char": "7", "image_url": None}, {"char": "7", "image_url": None}, {"char": "7", "image_url": None}], payouts
    )
    assert res is not None
    assert res["name"] == "JACKPOT"

    # 不成立
    res = evaluate_slot_spin(
        [{"char": "7", "image_url": None}, {"char": "7", "image_url": None}, {"char": "A", "image_url": None}], payouts
    )
    assert res is None


def test_evaluate_slot_spin_any_match():
    payouts = [
        {"pattern": ["🍒", "🍒", "ANY"], "name": "CHERRY_2", "score": 10},
    ]

    # 成立
    res = evaluate_slot_spin(
        [{"char": "🍒", "image_url": None}, {"char": "🍒", "image_url": None}, {"char": "🍇", "image_url": None}],
        payouts,
    )
    assert res is not None
    assert res["name"] == "CHERRY_2"
