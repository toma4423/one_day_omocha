from src.utils.roulette import (
    DEFAULT_ROULETTE_CONFIG,
    migrate_roulette_config,
    pick_roulette_winner,
    validate_roulette_config,
)


def test_pick_roulette_winner():
    # 重みが1つの場合、必ずその項目が選ばれること
    items = [{"label": "Win", "weight": 100, "color": "#000", "enabled": True}]
    winner = pick_roulette_winner(items)
    assert winner["label"] == "Win"

    # 重み0の項目が選ばれないこと
    items = [
        {"label": "Never", "weight": 0, "color": "#000", "enabled": True},
        {"label": "Always", "weight": 10, "color": "#FFF", "enabled": True},
    ]
    for _ in range(100):
        winner = pick_roulette_winner(items)
        assert winner["label"] == "Always"

def test_pick_roulette_winner_with_disabled():
    # 有効な項目のみが選ばれること
    items = [
        {"id": "1", "label": "Disabled", "weight": 100, "color": "#000", "enabled": False},
        {"id": "2", "label": "Enabled", "weight": 1, "color": "#FFF", "enabled": True},
    ]
    for _ in range(100):
        winner = pick_roulette_winner(items)
        assert winner["label"] == "Enabled"


def test_validate_roulette_config():
    valid_config = {
        "title": "My Roulette",
        "items": [{"label": "A", "weight": 10, "enabled": True}],
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
    # 整数に変換されていること
    assert isinstance(migrated["items"][0]["weight"], int)
