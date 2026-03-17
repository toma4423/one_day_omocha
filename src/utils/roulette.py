import random
from typing import Any

from pydantic import BaseModel


class RouletteItem(BaseModel):
    id: str
    label: str
    weight: int = 0
    color: str = "#CCCCCC"
    enabled: bool = True


class RouletteConfig(BaseModel):
    title: str = "カスタムルーレット"
    items: list[RouletteItem] = []
    sound_enabled: bool = True


DEFAULT_ROULETTE_CONFIG = RouletteConfig(
    title="カスタムルーレット",
    items=[
        RouletteItem(id="item_1", label="大吉", weight=10, color="#FF4B4B", enabled=True),
        RouletteItem(id="item_2", label="吉", weight=30, color="#FF8F8F", enabled=True),
        RouletteItem(id="item_3", label="中吉", weight=20, color="#FFD700", enabled=True),
        RouletteItem(id="item_4", label="小吉", weight=20, color="#6ED3FF", enabled=True),
        RouletteItem(id="item_5", label="末吉", weight=15, color="#A0A0A0", enabled=True),
        RouletteItem(id="item_6", label="凶", weight=5, color="#333333", enabled=True),
    ],
    sound_enabled=True,
)

COLOR_PRESETS = {
    "ビビッド": ["#FF4B4B", "#FFD700", "#6ED3FF", "#4CAF50", "#9C27B0", "#FF9800"],
    "パステル": ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#F3B0C3"],
    "モノトーン": ["#333333", "#666666", "#999999", "#CCCCCC", "#EEEEEE", "#F5F5F5"],
    "和風": ["#D75455", "#EAB333", "#4B61BA", "#567835", "#7051AA", "#4A4B4D"],
}


def pick_roulette_winner(items: list[RouletteItem]) -> RouletteItem:
    """有効な項目の中から重みに基づいて一つ抽選します。"""
    active_items = [item for item in items if item.enabled]
    if not active_items:
        raise ValueError("抽選対象の有効な項目が空です。")

    weights = [item.weight for item in active_items]
    return random.choices(active_items, weights=weights, k=1)[0]


def apply_color_preset(items: list[RouletteItem], preset_name: str) -> list[RouletteItem]:
    """選択されたプリセットカラーを項目に順番に適用します。"""
    if preset_name not in COLOR_PRESETS or not items:
        return items

    colors = COLOR_PRESETS[preset_name]
    new_items = []
    for i, item in enumerate(items):
        new_item = item.model_copy()
        new_item.color = colors[i % len(colors)]
        new_items.append(new_item)
    return new_items


def migrate_roulette_config(config_data: Any) -> RouletteConfig:
    """古い形式や不完全なデータから設定を最新の形式に復元します。"""
    if not config_data:
        return DEFAULT_ROULETTE_CONFIG

    try:
        if isinstance(config_data, dict):
            return RouletteConfig(**config_data)
        return DEFAULT_ROULETTE_CONFIG
    except Exception:
        return DEFAULT_ROULETTE_CONFIG
