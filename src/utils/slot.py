import random
from typing import Any

# デフォルト設定
# 図柄（シンボル）とその重み（出現確率に影響）
DEFAULT_SYMBOLS = [
    {"char": "🍒", "weight": 10.0},
    {"char": "🍋", "weight": 8.0},
    {"char": "🍉", "weight": 6.0},
    {"char": "🔔", "weight": 4.0},
    {"char": "⭐", "weight": 2.0},
    {"char": "7️⃣", "weight": 1.0},
]

DEFAULT_PAYOUTS = [
    {"pattern": ["7️⃣", "7️⃣", "7️⃣"], "name": "超大当り (777)", "score": 1000},
    {"pattern": ["⭐", "⭐", "⭐"], "name": "大当り (STAR)", "score": 500},
    {"pattern": ["🔔", "🔔", "🔔"], "name": "ベル", "score": 100},
    {"pattern": ["🍉", "🍉", "🍉"], "name": "スイカ", "score": 50},
    {"pattern": ["🍋", "🍋", "🍋"], "name": "レモン", "score": 20},
    {"pattern": ["🍒", "🍒", "🍒"], "name": "チェリー", "score": 10},
    {"pattern": ["🍒", "🍒", "ANY"], "name": "ミニチェリー", "score": 2},
]


def spin_reels(symbol_data: list[dict[str, Any]], count: int = 3) -> list[str]:
    """
    リールを回転させ、重みに基づいてランダムな出目を取得します。
    """
    if not symbol_data:
        return []

    # 互換性チェック: 文字列リストが渡された場合
    if isinstance(symbol_data[0], str):
        return [random.choice(symbol_data) for _ in range(count)]

    chars = [s["char"] for s in symbol_data]
    weights = [s.get("weight", 1.0) for s in symbol_data]

    # random.choices はリストを返す
    return random.choices(chars, weights=weights, k=count)


def evaluate_slot_spin(result: list[str], payouts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    出目を判定し、成立した役を返します。
    """
    if not result:
        return None

    for payout in payouts:
        pattern = payout["pattern"]
        if len(pattern) != len(result):
            continue

        match = True
        for i in range(len(pattern)):
            if pattern[i] == "ANY":
                continue
            if pattern[i] != result[i]:
                match = False
                break

        if match:
            return payout

    return None


def get_slot_config(storage_data: dict[str, Any] | None) -> dict[str, Any]:
    """
    ストレージデータから設定を取得、またはデフォルトを返します。
    """
    if not storage_data:
        return {"symbols": DEFAULT_SYMBOLS, "payouts": DEFAULT_PAYOUTS}

    symbols = storage_data.get("symbols", DEFAULT_SYMBOLS)

    # 互換性マイグレーション: リスト[str] を リスト[dict] に変換
    if symbols and isinstance(symbols[0], str):
        symbols = [{"char": s, "weight": 1.0} for s in symbols]

    return {
        "symbols": symbols,
        "payouts": storage_data.get("payouts", DEFAULT_PAYOUTS),
    }
