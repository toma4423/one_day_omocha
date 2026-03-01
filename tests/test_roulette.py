from src.utils.roulette import (
    DEFAULT_ROULETTE_CONFIG,
    migrate_roulette_config,
    normalize_weights,
    pick_roulette_winner,
    validate_roulette_config,
)


def test_pick_roulette_winner():
    # 重みが1つの場合、必ずその項目が選ばれること
    items = [{"label": "Win", "weight": 100.0, "color": "#000"}]
    winner = pick_roulette_winner(items)
    assert winner["label"] == "Win"

    # 重み0の項目が選ばれないこと（多数回試行）
    items = [
        {"label": "Never", "weight": 0.0, "color": "#000"},
        {"label": "Always", "weight": 10.0, "color": "#FFF"},
    ]
    for _ in range(100):
        winner = pick_roulette_winner(items)
        assert winner["label"] == "Always"


def test_normalize_weights_scaling():
    # 10, 30 -> 25%, 75%
    items = [
        {"label": "A", "weight": 10.0, "color": "#000"},
        {"label": "B", "weight": 30.0, "color": "#000"},
    ]
    normalized = normalize_weights(items)
    assert normalized[0]["weight"] == 25.0
    assert normalized[1]["weight"] == 75.0


def test_normalize_weights_zero_total():
    # ... (existing code)
    # 全ての重みが0の場合、均等に割り振られること
    items = [
        {"label": "A", "weight": 0.0, "color": "#000"},
        {"label": "B", "weight": 0.0, "color": "#000"},
    ]
    normalized = normalize_weights(items)
    assert normalized[0]["weight"] == 50.0
    assert normalized[1]["weight"] == 50.0


def test_validate_roulette_config():
    # 正常系
    valid_config = {
        "title": "My Roulette",
        "items": [{"label": "A", "weight": 10.0}],
    }
    is_valid, msg = validate_roulette_config(valid_config)
    assert is_valid is True

    # 異常系：項目リストなし
    invalid_config = {"title": "No Items"}
    is_valid, msg = validate_roulette_config(invalid_config)
    assert is_valid is False
    assert "項目リスト" in msg

    # 異常系：無効な重み
    invalid_config = {
        "items": [{"label": "A", "weight": -1.0}],
    }
    is_valid, msg = validate_roulette_config(invalid_config)
    assert is_valid is False
    assert "重みが無効" in msg


def test_migrate_roulette_config_missing_fields():
    # 不完全なデータからの移行
    legacy_data = {
        "items": [{"label": "A", "weight": 5.0}],
    }
    migrated = migrate_roulette_config(legacy_data)
    assert migrated["title"] == DEFAULT_ROULETTE_CONFIG["title"]  # デフォルト値が補完されること
    assert migrated["items"][0]["label"] == "A"
    assert migrated["items"][0]["color"] == "#CCCCCC"  # 色が補完されること
    assert migrated["sound_enabled"] is True
