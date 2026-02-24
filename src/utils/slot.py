import random
from typing import Any

# デフォルト設定
# 図柄（シンボル）：ID（数字）、識別子（文字）、重み、画像URL
DEFAULT_SYMBOLS = [
    {"id": 1, "char": "🍒", "weight": 10.0, "image_url": None},
    {"id": 2, "char": "🍋", "weight": 8.0, "image_url": None},
    {"id": 3, "char": "🍉", "weight": 6.0, "image_url": None},
    {"id": 4, "char": "🔔", "weight": 4.0, "image_url": None},
    {"id": 5, "char": "⭐", "weight": 2.0, "image_url": None},
    {"id": 6, "char": "7️⃣", "weight": 1.0, "image_url": None},
]

DEFAULT_PAYOUTS = [
    {"pattern": [6, 6, 6], "name": "超大当り (777)", "score": 1000},
    {"pattern": [5, 5, 5], "name": "大当り (STAR)", "score": 500},
    {"pattern": [4, 4, 4], "name": "ベル", "score": 100},
    {"pattern": [3, 3, 3], "name": "スイカ", "score": 50},
    {"pattern": [2, 2, 2], "name": "レモン", "score": 20},
    {"pattern": [1, 1, 1], "name": "チェリー", "score": 10},
    {"pattern": [1, 1, "ANY"], "name": "ミニチェリー", "score": 2},
]

DEFAULT_SLOT_NAME = "標準スロット"


def spin_reels(symbol_data: list[dict[str, Any]], count: int = 3) -> list[dict[str, Any]]:
    """
    リールを回転させ、重みに基づいてランダムな出目（辞書のリスト）を取得します。
    """
    if not symbol_data:
        return []

    # 互換性チェック: 文字列リストが渡された場合
    if isinstance(symbol_data[0], str):
        return [
            {"id": i + 1, "char": random.choice(symbol_data), "weight": 1.0, "image_url": None} for i in range(count)
        ]

    weights = [s.get("weight", 1.0) for s in symbol_data]

    # random.choices はリストを返す
    return random.choices(symbol_data, weights=weights, k=count)


def evaluate_slot_spin(result: list[dict[str, Any]], payouts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    出目を判定し、成立した役を返します。
    ID（数字）ベースで判定を行います。
    """
    if not result:
        return None

    # 比較のためにIDのみのリストを作成
    result_ids = [s["id"] for s in result]

    for payout in payouts:
        pattern = payout["pattern"]
        if len(pattern) != len(result_ids):
            continue

        match = True
        for i in range(len(pattern)):
            if pattern[i] == "ANY":
                continue
            # IDによる比較
            if pattern[i] != result_ids[i]:
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
        return {
            "name": DEFAULT_SLOT_NAME,
            "symbols": DEFAULT_SYMBOLS,
            "payouts": DEFAULT_PAYOUTS,
        }

    symbols = storage_data.get("symbols", DEFAULT_SYMBOLS)
    payouts = storage_data.get("payouts", DEFAULT_PAYOUTS)

    # 互換性マイグレーション
    if symbols:
        # 文字列リスト形式からの変換
        if isinstance(symbols[0], str):
            symbols = [{"id": i + 1, "char": s, "weight": 1.0, "image_url": None} for i, s in enumerate(symbols)]

        # IDフィールドがない場合の追加
        for i, s in enumerate(symbols):
            if isinstance(s, dict) and "id" not in s:
                s["id"] = i + 1
            if isinstance(s, dict) and "image_url" not in s:
                s["image_url"] = None

    # 役パターンのマイグレーション (charベースからidベースへ)
    char_to_id = {s["char"]: s["id"] for s in symbols}
    for p in payouts:
        new_pattern = []
        for item in p["pattern"]:
            if isinstance(item, str) and item in char_to_id:
                new_pattern.append(char_to_id[item])
            else:
                new_pattern.append(item)
        p["pattern"] = new_pattern

    return {
        "name": storage_data.get("name", DEFAULT_SLOT_NAME),
        "symbols": symbols,
        "payouts": payouts,
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

    results = []
    total_hit_prob = 0.0

    # 図柄が少なければ（例: 15個以下）、総当たりで正確に計算可能
    if len(symbol_data) <= 15:
        pattern_counts: dict[str, float] = {p["name"]: 0.0 for p in payouts}

        # 3リールの全組合せの確率を合計
        for s1 in symbol_data:
            for s2 in symbol_data:
                for s3 in symbol_data:
                    prob = (s1["weight"] / total_weight) * (s2["weight"] / total_weight) * (s3["weight"] / total_weight)
                    combo_ids = [s1["id"], s2["id"], s3["id"]]

                    for p in payouts:
                        pattern = p["pattern"]
                        is_match = True
                        for i in range(3):
                            if pattern[i] != "ANY" and pattern[i] != combo_ids[i]:
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
        # 図柄が多い場合は近似（IDベース）
        id_probs = {s["id"]: s["weight"] / total_weight for s in symbol_data}
        for p in payouts:
            prob = 1.0
            for item in p["pattern"]:
                if item == "ANY":
                    prob *= 1.0
                else:
                    prob *= id_probs.get(item, 0.0)

            rate = prob * 100
            results.append({"name": p["name"], "rate": rate})
            total_hit_prob += prob

    return {
        "hit_rates": results,
        "total_hit_rate": total_hit_prob * 100,
        "miss_rate": max(0.0, (1.0 - total_hit_prob) * 100),
    }


def solve_weights_from_targets(
    symbol_data: list[dict[str, Any]],
    payouts: list[dict[str, Any]],
    targets: dict[str, float],
    total_hit_rate: float | None = None,
) -> list[dict[str, Any]]:
    """
    目標とする役の出現確率（%）から、図柄の重みを逆算して更新します。
    """
    actual_targets = targets.copy()
    sum_targets = sum(targets.values())

    if total_hit_rate is not None and sum_targets > 0:
        scale = total_hit_rate / sum_targets
        for name in actual_targets:
            actual_targets[name] *= scale
    elif sum_targets > 100.0:
        scale = 95.0 / sum_targets
        for name in actual_targets:
            actual_targets[name] *= scale

    # IDベースで必要な確率を計算
    required_probs: dict[Any, float] = {s["id"]: 0.0 for s in symbol_data}

    for p in payouts:
        target_rate = actual_targets.get(p["name"], 0.0) / 100.0
        if target_rate <= 0:
            continue

        pattern = p["pattern"]
        unique_ids = [c for s in [set(pattern)] for c in s if c != "ANY"]

        if len(unique_ids) == 1:
            sym_id = unique_ids[0]
            count = pattern.count(sym_id)
            p_val = target_rate ** (1.0 / count)
            required_probs[sym_id] = max(required_probs[sym_id], p_val)

    total_req = sum(required_probs.values())
    max_allowed = 0.98

    if total_req > max_allowed:
        scale = max_allowed / total_req
        for sym_id in required_probs:
            required_probs[sym_id] *= scale
        total_req = max_allowed

    remaining_prob = 1.0 - total_req
    unassigned_symbols = [s["id"] for s in symbol_data if required_probs[s["id"]] < 0.01]

    if unassigned_symbols:
        p_extra = remaining_prob / len(unassigned_symbols)
        for sym_id in unassigned_symbols:
            required_probs[sym_id] += p_extra
    else:
        p_extra = remaining_prob / len(symbol_data)
        for sym_id in required_probs:
            required_probs[sym_id] += p_extra

    new_symbol_data = []
    for s in symbol_data:
        new_s = s.copy()
        new_s["weight"] = max(0.1, round(required_probs[s["id"]] * 1000, 1))
        new_symbol_data.append(new_s)

    return new_symbol_data
