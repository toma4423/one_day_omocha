from src.utils.parallel_counter import (
    add_counter,
    migrate_parallel_counter_data,
    remove_counter,
    update_counter_name,
    update_counter_value,
)


def test_update_counter_value():
    items = [{"id": "a", "name": "Item", "value": 10}]
    # 加算
    items = update_counter_value(items, "a", 1)
    assert items[0]["value"] == 11
    # 減算
    items = update_counter_value(items, "a", -5)
    assert items[0]["value"] == 6


def test_update_counter_name():
    items = [{"id": "a", "name": "OldName", "value": 0}]
    items = update_counter_name(items, "a", "NewName")
    assert items[0]["name"] == "NewName"


def test_add_and_remove_counter():
    items = []
    # 追加
    items = add_counter(items)
    assert len(items) == 1
    added_id = items[0]["id"]

    # 削除
    items = remove_counter(items, added_id)
    assert len(items) == 0


def test_migrate_parallel_counter_data_fallback():
    # 不正なデータのマイグレーション
    bad_data = "not a list"
    migrated = migrate_parallel_counter_data(bad_data)
    assert len(migrated) == 1
    assert migrated[0]["name"] == "新項目"
    assert migrated[0]["value"] == 0


def test_migrate_parallel_counter_data_full():
    # 部分的に欠けているデータのマイグレーション
    partial_data = [{"name": "Partial"}]
    migrated = migrate_parallel_counter_data(partial_data)
    assert migrated[0]["name"] == "Partial"
    assert "id" in migrated[0]
    assert migrated[0]["value"] == 0
