import time
from typing import Any

from pydantic import BaseModel


class ParallelCounterItem(BaseModel):
    """並列カウンターの個別の項目を定義するモデル"""

    id: str
    name: str = "新項目"
    value: int = 0


class ParallelCounterSession(BaseModel):
    """並列カウンターのセッション全体を定義するモデル"""

    items: list[ParallelCounterItem] = []


def create_empty_counter(counter_id: str) -> ParallelCounterItem:
    """新しい空のカウンター項目を作成します。"""
    return ParallelCounterItem(id=counter_id, name="新項目", value=0)


def update_counter_value(items: list[ParallelCounterItem], counter_id: str, delta: int) -> list[ParallelCounterItem]:
    """指定されたカウンターの数値を増減させます。"""
    for item in items:
        if item.id == counter_id:
            item.value += delta
            break
    return items


def update_counter_name(items: list[ParallelCounterItem], counter_id: str, name: str) -> list[ParallelCounterItem]:
    """指定されたカウンターの名前を更新します。"""
    for item in items:
        if item.id == counter_id:
            item.name = name
            break
    return items


def add_counter(items: list[ParallelCounterItem]) -> list[ParallelCounterItem]:
    """新しいカウンターを追加します。IDは現在の要素数に基づいて生成します。"""
    timestamp = int(time.time() * 1000)
    new_id = f"cnt_{len(items)}_{timestamp}"
    items.append(create_empty_counter(new_id))
    return items


def remove_counter(items: list[ParallelCounterItem], counter_id: str) -> list[ParallelCounterItem]:
    """指定されたカウンターを削除します。"""
    return [item for item in items if item.id != counter_id]


def migrate_parallel_counter_data(data: Any) -> list[ParallelCounterItem]:
    """保存されたデータから最新のカウンターリスト形式へ移行・復元します。"""
    if not isinstance(data, list):
        return [create_empty_counter("cnt_default")]

    new_items = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        try:
            new_item = ParallelCounterItem(
                id=str(item.get("id", f"cnt_{i}")),
                name=str(item.get("name", "項目")),
                value=int(item.get("value", 0)),
            )
            new_items.append(new_item)
        except Exception:
            continue

    if not new_items:
        new_items = [create_empty_counter("cnt_default")]

    return new_items
