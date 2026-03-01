import random
from typing import Any, TypedDict


class RouletteItem(TypedDict):
    label: str
    weight: float
    color: str


class RouletteConfig(TypedDict):
    title: str
    items: list[RouletteItem]
    sound_enabled: bool


DEFAULT_ROULETTE_CONFIG: RouletteConfig = {
    "title": "カスタムルーレット",
    "items": [
        {"label": "大吉", "weight": 10.0, "color": "#FF4B4B"},
        {"label": "吉", "weight": 30.0, "color": "#FF8F8F"},
        {"label": "中吉", "weight": 20.0, "color": "#FFD700"},
        {"label": "小吉", "weight": 20.0, "color": "#6ED3FF"},
        {"label": "末吉", "weight": 15.0, "color": "#A0A0A0"},
        {"label": "凶", "weight": 5.0, "color": "#333333"},
    ],
    "sound_enabled": True,
}


def pick_roulette_winner(items: list[RouletteItem]) -> RouletteItem:
    """重みに基づいて項目を一つ抽選します。"""
    if not items:
        raise ValueError("抽選対象の項目が空です。")

    weights = [item["weight"] for item in items]
    return random.choices(items, weights=weights, k=1)[0]


def normalize_weights(items: list[RouletteItem]) -> list[RouletteItem]:
    """重みの合計が100%になるように調整します。"""
    if not items:
        return []

    new_items = [item.copy() for item in items]
    total = sum(float(item["weight"]) for item in new_items)

    if total <= 0:
        # 重みがすべて0または負の場合は均等に割り当て
        default_weight = 100.0 / len(new_items)
        for item in new_items:
            item["weight"] = round(default_weight, 2)
    else:
        # 100%換算にする
        for item in new_items:
            item["weight"] = round((float(item["weight"]) / total) * 100.0, 2)

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

    if not config:
        return new_config

    new_config["title"] = config.get("title", DEFAULT_ROULETTE_CONFIG["title"])
    new_config["sound_enabled"] = config.get("sound_enabled", DEFAULT_ROULETTE_CONFIG["sound_enabled"])

    items = config.get("items", [])
    if isinstance(items, list) and items:
        new_items = []
        for item in items:
            if isinstance(item, dict):
                new_item: RouletteItem = {
                    "label": str(item.get("label", "項目")),
                    "weight": float(item.get("weight", 1.0)),
                    "color": str(item.get("color", "#CCCCCC")),
                }
                new_items.append(new_item)
        if new_items:
            new_config["items"] = new_items

    return new_config
