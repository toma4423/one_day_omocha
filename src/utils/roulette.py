import random
import time
from typing import Any, TypedDict


class RouletteItem(TypedDict):
    id: str
    label: str
    weight: int
    color: str
    enabled: bool


class RouletteConfig(TypedDict):
    title: str
    items: list[RouletteItem]
    sound_enabled: bool


DEFAULT_ROULETTE_CONFIG: RouletteConfig = {
    "title": "カスタムルーレット",
    "items": [
        {"id": "item_1", "label": "大吉", "weight": 10, "color": "#FF4B4B", "enabled": True},
        {"id": "item_2", "label": "吉", "weight": 30, "color": "#FF8F8F", "enabled": True},
        {"id": "item_3", "label": "中吉", "weight": 20, "color": "#FFD700", "enabled": True},
        {"id": "item_4", "label": "小吉", "weight": 20, "color": "#6ED3FF", "enabled": True},
        {"id": "item_5", "label": "末吉", "weight": 15, "color": "#A0A0A0", "enabled": True},
        {"id": "item_6", "label": "凶", "weight": 5, "color": "#333333", "enabled": True},
    ],
    "sound_enabled": True,
}

COLOR_PRESETS = {
    "ビビッド": ["#FF4B4B", "#FFD700", "#6ED3FF", "#4CAF50", "#9C27B0", "#FF9800"],
    "パステル": ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#F3B0C3"],
    "モノトーン": ["#333333", "#666666", "#999999", "#CCCCCC", "#EEEEEE", "#F5F5F5"],
    "和風": ["#D75455", "#EAB333", "#4B61BA", "#567835", "#7051AA", "#4A4B4D"],
}


def pick_roulette_winner(items: list[RouletteItem]) -> RouletteItem:
    """有効な項目の中から重みに基づいて一つ抽選します。"""
    active_items = [item for item in items if item.get("enabled", True)]
    if not active_items:
        raise ValueError("抽選対象の有効な項目が空です。")

    weights = [item["weight"] for item in active_items]
    return random.choices(active_items, weights=weights, k=1)[0]


def apply_color_preset(items: list[RouletteItem], preset_name: str) -> list[RouletteItem]:
    """選択されたプリセットカラーを項目に順番に適用します。"""
    if preset_name not in COLOR_PRESETS or not items:
        return items

    colors = COLOR_PRESETS[preset_name]
    new_items = []
    for i, item in enumerate(items):
        new_item = item.copy()
        new_item["color"] = colors[i % len(colors)]
        new_items.append(new_item)
    return new_items


def validate_roulette_config(config: dict[str, Any]) -> tuple[bool, str]:
    """設定データの形式をチェックします。"""
    if not isinstance(config, dict):
        return False, "設定データが辞書形式ではありません。"

    items = config.get("items")
    if not isinstance(items, list) or not items:
        return False, "項目リストが正しくありません。"

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            return False, f"項目 {i + 1} が辞書形式ではありません。"
        if "label" not in item or "weight" not in item:
            return False, f"項目 {i + 1} に必要なキー（label, weight）がありません。"
        if not isinstance(item["weight"], (int, float)) or item["weight"] < 0:
            return False, f"項目 {i + 1} の重みが無効です。"

    return True, ""


def migrate_roulette_config(config: dict[str, Any]) -> RouletteConfig:
    """古い形式や不完全なデータから設定を最新の形式に復元します。"""
    new_config = DEFAULT_ROULETTE_CONFIG.copy()

    if not isinstance(config, dict):
        return new_config

    new_config["title"] = str(config.get("title", DEFAULT_ROULETTE_CONFIG["title"]))
    new_config["sound_enabled"] = bool(config.get("sound_enabled", DEFAULT_ROULETTE_CONFIG["sound_enabled"]))

    items = config.get("items", [])
    if isinstance(items, list) and items:
        new_items = []
        for i, item in enumerate(items):
            if isinstance(item, dict):
                # 重みの安全な変換 (floatも許容し、四捨五入して整数にする)
                raw_weight = item.get("weight", 1)
                try:
                    weight = int(round(float(raw_weight)))
                except (ValueError, TypeError):
                    weight = 1
                
                new_item: RouletteItem = {
                    "id": str(item.get("id", f"item_{int(time.time() * 1000)}_{i}")),
                    "label": str(item.get("label", f"項目 {i+1}")),
                    "weight": max(0, weight),
                    "color": str(item.get("color", "#CCCCCC")),
                    "enabled": bool(item.get("enabled", True)),
                }
                new_items.append(new_item)
        if new_items:
            new_config["items"] = new_items

    return new_config
