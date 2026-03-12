from src.utils.slot import (
    DEFAULT_PAYOUTS,
    DEFAULT_SYMBOLS,
    SlotConfig,
    SlotSymbol,
    evaluate_slot_spin,
    get_slot_config,
    spin_reels,
    validate_slot_config,
)


def test_spin_reels():
    config = SlotConfig(symbols=DEFAULT_SYMBOLS, payouts=DEFAULT_PAYOUTS)
    result = spin_reels(config)
    assert len(result) == 3
    assert all(isinstance(s, SlotSymbol) for s in result)


def test_evaluate_slot_spin_hit():
    # 777の出目を作成
    symbol_7 = SlotSymbol(id=6, char="7️⃣")
    result = [symbol_7, symbol_7, symbol_7]

    payout = evaluate_slot_spin(result, DEFAULT_PAYOUTS)
    assert payout is not None
    assert payout.name == "超大当り (777)"


def test_evaluate_slot_spin_miss():
    # バラバラの出目
    result = [
        SlotSymbol(id=1, char="🍒"),
        SlotSymbol(id=2, char="🍋"),
        SlotSymbol(id=6, char="7️⃣"),
    ]
    payout = evaluate_slot_spin(result, DEFAULT_PAYOUTS)
    assert payout is None


def test_validate_slot_config_valid():
    config_dict = {
        "name": "Test Slot",
        "symbols": [s.model_dump() for s in DEFAULT_SYMBOLS],
        "payouts": [p.model_dump() for p in DEFAULT_PAYOUTS],
    }
    is_valid, msg = validate_slot_config(config_dict)
    assert is_valid is True


def test_validate_slot_config_invalid():
    # 名前がない
    is_valid, msg = validate_slot_config({"name": ""})
    assert is_valid is False

    # 不正なID
    invalid_payouts = [p.model_dump() for p in DEFAULT_PAYOUTS]
    invalid_payouts[0]["pattern"] = [999, 999, 999]
    config_dict = {
        "name": "Invalid",
        "symbols": [s.model_dump() for s in DEFAULT_SYMBOLS],
        "payouts": invalid_payouts,
    }
    is_valid, msg = validate_slot_config(config_dict)
    assert is_valid is False


def test_get_slot_config_none():
    config = get_slot_config(None)
    assert config.name == "標準スロット"
    assert len(config.symbols) == len(DEFAULT_SYMBOLS)
