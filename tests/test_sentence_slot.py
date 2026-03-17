import hashlib

from src.utils.sentence_slot import (
    SentenceSlotConfig,
    migrate_sentence_slot_data,
    pick_random_item,
)


def test_pick_random_item_equal_probability():
    """項目の出現確率が均等であることを検証します（統計的テスト）。"""
    items = ["A", "B", "C", "D", "E"]
    iterations = 10000
    counts = {item: 0 for item in items}

    for _ in range(iterations):
        selected = pick_random_item(items)
        counts[selected] += 1

    # 期待値は 2000 (1/5)
    # ±5% の範囲内 (1900 - 2100) に収まっているか確認
    expected = iterations / len(items)
    tolerance = expected * 0.05

    for item in items:
        assert expected - tolerance <= counts[item] <= expected + tolerance


def test_migrate_sentence_slot_data_basic():
    """基本的なデータ移行が機能することを検証します。"""
    legacy_data = {
        "reels": [
            {"name": "Who", "items": ["User"]},
            {"name": "What", "items": ["Code"]},
            {"name": "How", "items": ["Write"]},
        ]
    }
    config = migrate_sentence_slot_data(legacy_data)
    assert config.reels[0].name == "Who"
    assert config.reels[0].items == ["User"]
    assert len(config.reels) == 3


def test_migrate_sentence_slot_data_invalid():
    """無効なデータが与えられた場合にデフォルト設定が返ることを検証します。"""
    assert migrate_sentence_slot_data(None).reels[0].name == "誰が"
    assert migrate_sentence_slot_data({"broken": "data"}).reels[0].name == "誰が"


def test_sentence_slot_config_defaults():
    """デフォルト設定が正しく初期化されることを検証します。"""
    config = SentenceSlotConfig()
    assert len(config.reels) == 3
    assert config.reels[0].name == "誰が"
    assert "猫が" in config.reels[0].items


def test_config_hash_consistency():
    """設定データのハッシュ値が一貫していることを検証します。"""
    config = SentenceSlotConfig()
    config_json = config.model_dump_json()
    hash1 = hashlib.md5(config_json.encode()).hexdigest()
    hash2 = hashlib.md5(config_json.encode()).hexdigest()
    assert hash1 == hash2
    assert len(hash1) == 32  # MD5 hash length
