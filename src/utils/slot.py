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


def calculate_probabilities(symbol_data: list[dict[str, Any]], payouts: list[dict[str, Any]]) -> dict[str, Any]:
    """
    現在の設定に基づき、各役の成立確率とハズレ確率を計算します。
    3リール固定の想定です。
    """
    if not symbol_data:
        return {"hit_rates": [], "total_hit_rate": 0.0, "miss_rate": 100.0}

    total_weight = sum(s["weight"] for s in symbol_data)
    if total_weight == 0:
        return {"hit_rates": [], "total_hit_rate": 0.0, "miss_rate": 100.0}

    # 各図柄の単体出現確率
    char_probs = {s["char"]: s["weight"] / total_weight for s in symbol_data}

    def get_prob(char: str) -> float:
        return float(char_probs.get(char, 0.0))

    results = []
    total_hit_prob = 0.0

    # 役は上から順に判定されるため、排他的な確率計算が必要だが、
    # 簡易化のため独立して計算しつつ、重複を避ける順序で評価する。
    # 実際のスロットと同様、役のリストの順序に従って「その役が成立する確率」を出す。

    # 厳密な計算（ANYを含むため）: すべての組み合わせ(N^3)をシミュレーションするか、
    # 役の優先度を考慮した計算を行う。ここでは実用的な近似または正確な総当たり（図柄が少なければ）

    # 図柄が少なければ（例: 10個以下）、総当たりで正確に計算可能
    if len(symbol_data) <= 15:
        pattern_counts: dict[str, float] = {}
        for p in payouts:
            pattern_counts[p["name"]] = 0.0

        # 3リールの全組合せの確率を合計
        for s1 in symbol_data:
            for s2 in symbol_data:
                for s3 in symbol_data:
                    prob = (s1["weight"] / total_weight) * (s2["weight"] / total_weight) * (s3["weight"] / total_weight)
                    combo = [s1["char"], s2["char"], s3["char"]]

                    for p in payouts:
                        pattern = p["pattern"]
                        is_match = True
                        for i in range(3):
                            if pattern[i] != "ANY" and pattern[i] != combo[i]:
                                is_match = False
                                break
                        if is_match:
                            pattern_counts[p["name"]] += prob
                            total_hit_prob += prob
                            break

        for p in payouts:
            rate = pattern_counts[p["name"]] * 100
            results.append({"name": p["name"], "rate": rate})

    else:
        # 図柄が多い場合は近似（ANYなし前提の単純計算など）
        for p in payouts:
            prob = 1.0
            for char in p["pattern"]:
                if char == "ANY":
                    prob *= 1.0
                else:
                    prob *= get_prob(char)

            # 簡易計算のため他との重複は無視（上位の役から引くなどの処理が必要）
            rate = prob * 100
            results.append({"name": p["name"], "rate": rate})
            total_hit_prob += prob

    return {
        "hit_rates": results,
        "total_hit_rate": total_hit_prob * 100,
        "miss_rate": max(0.0, (1.0 - total_hit_prob) * 100),
    }
