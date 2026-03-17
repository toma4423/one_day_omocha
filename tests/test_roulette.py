from src.utils.roulette import (
    DEFAULT_ROULETTE_CONFIG,
    RouletteItem,
    migrate_roulette_config,
    pick_roulette_winner,
)


def test_pick_roulette_winner():
    # 重みが1つの場合、必ずその項目が選ばれること
    items = [RouletteItem(id="1", label="Win", weight=100, color="#000", enabled=True)]
    winner = pick_roulette_winner(items)
    assert winner.label == "Win"

    # 重み0の項目が選ばれないこと
    items = [
        RouletteItem(id="1", label="Never", weight=0, color="#000", enabled=True),
        RouletteItem(id="2", label="Always", weight=10, color="#FFF", enabled=True),
    ]
    for _ in range(100):
        winner = pick_roulette_winner(items)
        assert winner.label == "Always"


def test_pick_roulette_winner_with_disabled():
    # 有効な項目のみが選ばれること
    items = [
        RouletteItem(id="1", label="Disabled", weight=100, color="#000", enabled=False),
        RouletteItem(id="2", label="Enabled", weight=1, color="#FFF", enabled=True),
    ]
    for _ in range(100):
        winner = pick_roulette_winner(items)
        assert winner.label == "Enabled"


def test_migrate_roulette_config_basic():
    # 標準的な移行
    legacy_data = {
        "items": [{"id": "1", "label": "A", "weight": 5}],
    }
    migrated = migrate_roulette_config(legacy_data)
    assert migrated.title == DEFAULT_ROULETTE_CONFIG.title
    assert migrated.items[0].label == "A"
    assert migrated.items[0].enabled is True
    assert isinstance(migrated.items[0].weight, int)


def test_migrate_roulette_config_invalid_data():
    # 完全に壊れたデータ
    assert migrate_roulette_config(None).title == DEFAULT_ROULETTE_CONFIG.title
    assert migrate_roulette_config([]).title == DEFAULT_ROULETTE_CONFIG.title
    # Pydanticによりバリデーションエラー時はデフォルトが返る
    assert migrate_roulette_config({"items": "not a list"}).items == DEFAULT_ROULETTE_CONFIG.items
