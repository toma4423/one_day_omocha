from src.utils.slot import (
    calculate_probabilities,
    evaluate_slot_spin,
    migrate_slot_config,
    resolve_pattern_to_chars,
    solve_weights_from_denominators,
    spin_reels,
    validate_slot_config,
)


def test_validate_slot_config_success():
    valid_config = {
        "name": "Test",
        "symbols": [{"id": 1, "char": "A"}],
        "payouts": [{"name": "W", "pattern": [1, 1, 1], "denominator": 10.0}],
    }
    is_valid, msg = validate_slot_config(valid_config)
    assert is_valid is True


def test_validate_slot_config_fail_duplicate():
    invalid_config = {
        "name": "Test",
        "symbols": [{"id": 1, "char": "A"}, {"id": 1, "char": "B"}],
        "payouts": [{"name": "W", "pattern": [1, 1, 1]}],
    }
    # IDの重複チェック
    invalid_config["symbols"][1]["id"] = 1
    is_valid, msg = validate_slot_config(invalid_config)
    assert is_valid is False
    assert "IDが重複" in msg


def test_migrate_slot_config_denominator():
    legacy_config = {
        "symbols": [{"char": "7"}],
        "payouts": [{"name": "BIG", "pattern": ["7", "7", "7"]}],
    }
    migrated = migrate_slot_config(legacy_config)
    assert "denominator" in migrated["payouts"][0]
    assert migrated["payouts"][0]["denominator"] == 0.0


def test_solve_weights_from_denominators():
    symbols = [
        {"id": 1, "char": "7", "weight": 1.0},
        {"id": 2, "char": "Blank", "weight": 1.0},
    ]
    payouts = [
        {"name": "JACKPOT", "pattern": [1, 1, 1], "denominator": 8.0},  # 1/8 = 12.5%
    ]

    new_symbols = solve_weights_from_denominators(symbols, payouts)
    probs = calculate_probabilities(new_symbols, payouts)

    # 逆算後の確率が 1/8 (12.5%) に近いことを確認
    assert 11.0 <= probs["hit_rates"][0]["rate"] <= 14.0


def test_resolve_pattern_to_chars():
    symbols = [{"id": 1, "char": "🍒"}]
    assert resolve_pattern_to_chars([1, "ANY", 1], symbols) == ["🍒", "ANY", "🍒"]


def test_spin_reels():
    symbol_data = [{"id": 1, "char": "A", "weight": 1.0}]
    result = spin_reels(symbol_data, 3)
    assert len(result) == 3
    assert result[0]["char"] == "A"


def test_evaluate_slot_spin_any():
    payouts = [{"pattern": [1, "ANY", "ANY"], "name": "CHERRY", "score": 2}]
    result = evaluate_slot_spin([{"id": 1}, {"id": 2}, {"id": 3}], payouts)
    assert result is not None
    assert result["name"] == "CHERRY"
