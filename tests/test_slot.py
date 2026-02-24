from src.utils.slot import evaluate_slot_spin, spin_reels


def test_spin_reels():
    symbol_data = [
        {"char": "A", "weight": 1},
        {"char": "B", "weight": 1},
        {"char": "C", "weight": 1},
    ]
    result = spin_reels(symbol_data, 3)
    assert len(result) == 3
    chars = [s["char"] for s in symbol_data]
    for s in result:
        assert s in chars


def test_spin_reels_weighted():
    # 重みが極端な場合
    symbol_data = [
        {"char": "A", "weight": 1000},
        {"char": "B", "weight": 0},
    ]
    result = spin_reels(symbol_data, 10)
    for s in result:
        assert s == "A"


def test_evaluate_slot_spin_exact_match():
    payouts = [
        {"pattern": ["7", "7", "7"], "name": "JACKPOT", "score": 1000},
        {"pattern": ["A", "A", "A"], "name": "AAA", "score": 100},
    ]

    # 成立
    res = evaluate_slot_spin(["7", "7", "7"], payouts)
    assert res is not None
    assert res["name"] == "JACKPOT"

    # 成立
    res = evaluate_slot_spin(["A", "A", "A"], payouts)
    assert res is not None
    assert res["name"] == "AAA"

    # 不成立
    res = evaluate_slot_spin(["7", "7", "A"], payouts)
    assert res is None


def test_evaluate_slot_spin_any_match():
    payouts = [
        {"pattern": ["🍒", "🍒", "ANY"], "name": "CHERRY_2", "score": 10},
    ]

    # 成立
    res = evaluate_slot_spin(["🍒", "🍒", "🍇"], payouts)
    assert res is not None
    assert res["name"] == "CHERRY_2"

    # 成立
    res = evaluate_slot_spin(["🍒", "🍒", "🍒"], payouts)
    assert res is not None
    assert res["name"] == "CHERRY_2"

    # 不成立
    res = evaluate_slot_spin(["🍒", "🍇", "🍒"], payouts)
    assert res is None


def test_evaluate_slot_spin_order():
    # 上から順に評価されることを確認
    payouts = [
        {"pattern": ["A", "A", "A"], "name": "AAA_PRIORITY", "score": 200},
        {"pattern": ["A", "A", "ANY"], "name": "AA_ANY", "score": 100},
    ]

    res = evaluate_slot_spin(["A", "A", "A"], payouts)
    assert res is not None
    assert res["name"] == "AAA_PRIORITY"
