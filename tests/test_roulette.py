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
    items = [{"label": "Win", "weight": 100.0, "color": "#000", "enabled": True}]
    winner = pick_roulette_winner(items)
    assert winner["label"] == "Win"

    # 重み0の項目が選ばれないこと
    items = [
        {"label": "Never", "weight": 0.0, "color": "#000", "enabled": True},
        {"label": "Always", "weight": 10.0, "color": "#FFF", "enabled": True},
    ]
    for _ in range(100):
        winner = pick_roulette_winner(items)
        assert winner["label"] == "Always"

def test_pick_roulette_winner_with_disabled():
    # 有効な項目のみが選ばれること
    items = [
        {"id": "1", "label": "Disabled", "weight": 100.0, "color": "#000", "enabled": False},
        {"id": "2", "label": "Enabled", "weight": 1.0, "color": "#FFF", "enabled": True},
    ]
    for _ in range(100):
        winner = pick_roulette_winner(items)
        assert winner["label"] == "Enabled"


def test_normalize_weights():
    # 10, 30 -> 25%, 75%
    items = [
        {"label": "A", "weight": 10.0, "color": "#000", "enabled": True},
        {"label": "B", "weight": 30.0, "color": "#000", "enabled": True},
    ]
    normalized = normalize_weights(items)
    assert normalized[0]["weight"] == 25.0
    assert normalized[1]["weight"] == 75.0

def test_normalize_weights_with_disabled():
    # 無効な項目がある場合、有効な項目だけで100%にする
    items = [
        {"label": "A", "weight": 10.0, "color": "#000", "enabled": True},
        {"label": "B", "weight": 10.0, "color": "#000", "enabled": False},
    ]
    normalized = normalize_weights(items)
    assert normalized[0]["weight"] == 100.0
    assert normalized[1]["enabled"] is False


def test_equalize_weights():
    # 3つの項目 -> 合計 100.0%
    items = [
        {"label": "A", "weight": 10.0, "color": "#000", "enabled": True},
        {"label": "B", "weight": 50.0, "color": "#000", "enabled": True},
        {"label": "C", "weight": 0.0, "color": "#000", "enabled": True},
    ]
    equalized = equalize_weights(items)
    assert sum(it["weight"] for it in equalized) == 100.0
    for item in equalized:
        assert 33.33 <= item["weight"] <= 33.34

def test_equalize_weights_with_disabled():
    # 有効な項目だけを均等にする
    items = [
        {"label": "A", "weight": 10.0, "color": "#000", "enabled": True},
        {"label": "B", "weight": 50.0, "color": "#000", "enabled": True},
        {"label": "C", "weight": 0.0, "color": "#000", "enabled": False},
    ]
    equalized = equalize_weights(items)
    assert equalized[0]["weight"] == 50.0
    assert equalized[1]["weight"] == 50.0
    assert equalized[2]["weight"] == 0.0


def test_validate_roulette_config():
    valid_config = {
        "title": "My Roulette",
        "items": [{"label": "A", "weight": 10.0, "enabled": True}],
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
    assert migrated["items"][0]["enabled"] is True
