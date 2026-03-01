import time
from typing import Any, TypedDict


class CounterItem(TypedDict):
    id: str
    name: str
    value: int


def create_empty_counter(counter_id: str) -> CounterItem:
    """新しい空のカウンター項目を作成します。"""
    return {"id": counter_id, "name": "新項目", "value": 0}


def update_counter_value(items: list[CounterItem], counter_id: str, delta: int) -> list[CounterItem]:
    """指定されたカウンターの数値を増減させます。"""
    for item in items:
        if item["id"] == counter_id:
            item["value"] += delta
            break
    return items


def update_counter_name(items: list[CounterItem], counter_id: str, name: str) -> list[CounterItem]:
    """指定されたカウンターの名前を更新します。"""
    for item in items:
        if item["id"] == counter_id:
            item["name"] = name
            break
    return items


def add_counter(items: list[CounterItem]) -> list[CounterItem]:
    """新しいカウンターを追加します。IDは現在の要素数に基づいて生成します。"""
    timestamp = int(time.time() * 1000)
    new_id = f"cnt_{len(items)}_{timestamp}"
    items.append(create_empty_counter(new_id))
    return items


def remove_counter(items: list[CounterItem], counter_id: str) -> list[CounterItem]:
    """指定されたカウンターを削除します。"""
    return [item for item in items if item["id"] != counter_id]


def migrate_parallel_counter_data(data: Any) -> list[CounterItem]:
    """保存されたデータから最新のカウンターリスト形式へ移行・復元します。"""
    if not isinstance(data, list):
        return [create_empty_counter("cnt_default")]

    new_items = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        new_item: CounterItem = {
            "id": str(item.get("id", f"cnt_{i}")),
            "name": str(item.get("name", "項目")),
            "value": int(item.get("value", 0)),
        }
        new_items.append(new_item)

    if not new_items:
        new_items = [create_empty_counter("cnt_default")]

    return new_items
