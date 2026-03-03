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


def test_migrate_roulette_config_basic():
    # 標準的な移行
    legacy_data = {
        "items": [{"label": "A", "weight": 5}],
    }
    migrated = migrate_roulette_config(legacy_data)
    assert migrated["title"] == DEFAULT_ROULETTE_CONFIG["title"]
    assert migrated["items"][0]["label"] == "A"
    assert migrated["items"][0]["enabled"] is True
    assert isinstance(migrated["items"][0]["weight"], int)


def test_migrate_roulette_config_legacy_float():
    # float形式からの移行と丸め
    legacy_data = {
        "items": [
            {"label": "A", "weight": 10.6},  # -> 11
            {"label": "B", "weight": "20.4"},  # -> 20 (文字列float)
        ],
    }
    migrated = migrate_roulette_config(legacy_data)
    assert migrated["items"][0]["weight"] == 11
    assert migrated["items"][1]["weight"] == 20
    assert all(isinstance(it["weight"], int) for it in migrated["items"])


def test_migrate_roulette_config_missing_fields():
    # 欠落フィールドの補完
    legacy_data = {
        "title": "New Title",
        "items": [
            {"label": "A"}  # weight, id, color, enabled が欠落
        ],
    }
    migrated = migrate_roulette_config(legacy_data)
    item = migrated["items"][0]
    assert migrated["title"] == "New Title"
    assert item["weight"] == 1  # デフォルト
    assert item["enabled"] is True
    assert "id" in item
    assert item["color"] == "#CCCCCC"


def test_migrate_roulette_config_invalid_data():
    # 完全に壊れたデータ
    assert migrate_roulette_config(None)["title"] == DEFAULT_ROULETTE_CONFIG["title"]
    assert migrate_roulette_config([])["title"] == DEFAULT_ROULETTE_CONFIG["title"]
    assert migrate_roulette_config({"items": "not a list"})["items"] == DEFAULT_ROULETTE_CONFIG["items"]
