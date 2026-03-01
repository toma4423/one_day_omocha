from src.utils.roulette import (
    DEFAULT_ROULETTE_CONFIG,
    equalize_weights,
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

    # 重み0の項目が選ばれないこと
    items = [
        {"label": "Never", "weight": 0.0, "color": "#000"},
        {"label": "Always", "weight": 10.0, "color": "#FFF"},
    ]
    for _ in range(100):
        winner = pick_roulette_winner(items)
        assert winner["label"] == "Always"


def test_normalize_weights():
    # 10, 30 -> 25%, 75%
    items = [
        {"label": "A", "weight": 10.0, "color": "#000"},
        {"label": "B", "weight": 30.0, "color": "#000"},
    ]
    normalized = normalize_weights(items)
    assert normalized[0]["weight"] == 25.0
    assert normalized[1]["weight"] == 75.0


def test_equalize_weights():
    # 3つの項目 -> 各 33.33%
    items = [
        {"label": "A", "weight": 10.0, "color": "#000"},
        {"label": "B", "weight": 50.0, "color": "#000"},
        {"label": "C", "weight": 0.0, "color": "#000"},
    ]
    equalized = equalize_weights(items)
    assert equalized[0]["weight"] == 33.33
    assert equalized[1]["weight"] == 33.33
    assert equalized[2]["weight"] == 33.33


def test_validate_roulette_config():
    valid_config = {
        "title": "My Roulette",
        "items": [{"label": "A", "weight": 10.0}],
    }
    is_valid, msg = validate_roulette_config(valid_config)
    assert is_valid is True

    invalid_config = {"items": []}
    is_valid, msg = validate_roulette_config(invalid_config)
    assert is_valid is False


def test_migrate_roulette_config():
    legacy_data = {
        "items": [{"label": "A", "weight": 5.0}],
    }
    migrated = migrate_roulette_config(legacy_data)
    assert migrated["title"] == DEFAULT_ROULETTE_CONFIG["title"]
    assert migrated["items"][0]["label"] == "A"
    assert migrated["items"][0]["color"] == "#CCCCCC"
