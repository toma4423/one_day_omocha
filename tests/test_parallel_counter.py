from src.utils.parallel_counter import (
    ParallelCounterItem,
    add_counter,
    create_empty_counter,
    migrate_parallel_counter_data,
    remove_counter,
    update_counter_name,
    update_counter_value,
)


def test_create_empty_counter():
    counter = create_empty_counter("test_id")
    assert counter.id == "test_id"
    assert counter.name == "新項目"
    assert counter.value == 0


def test_update_counter_value():
    items = [ParallelCounterItem(id="c1", name="A", value=10)]
    items = update_counter_value(items, "c1", 5)
    assert items[0].value == 15
    items = update_counter_value(items, "c1", -3)
    assert items[0].value == 12


def test_update_counter_name():
    items = [ParallelCounterItem(id="c1", name="A", value=10)]
    items = update_counter_name(items, "c1", "Updated")
    assert items[0].name == "Updated"


def test_add_remove_counter():
    items = []
    items = add_counter(items)
    assert len(items) == 1
    cid = items[0].id
    items = remove_counter(items, cid)
    assert len(items) == 0


def test_migrate_data():
    legacy_data = [{"id": "old", "name": "Old", "value": 5}]
    items = migrate_parallel_counter_data(legacy_data)
    assert len(items) == 1
    assert items[0].id == "old"
    assert items[0].value == 5
