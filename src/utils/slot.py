import random
from typing import Any

# デフォルト設定
DEFAULT_SYMBOLS = [
    {"id": 1, "char": "🍒", "weight": 15.0, "image_url": None},
    {"id": 2, "char": "🍋", "weight": 10.0, "image_url": None},
    {"id": 3, "char": "🍉", "weight": 7.0, "image_url": None},
    {"id": 4, "char": "🔔", "weight": 5.0, "image_url": None},
    {"id": 5, "char": "⭐", "weight": 3.0, "image_url": None},
    {"id": 6, "char": "7️⃣", "weight": 2.0, "image_url": None},
]

# デフォルトの役設定
DEFAULT_PAYOUTS = [
    {"pattern": [6, 6, 6], "name": "超大当り (777)", "score": 0, "denominator": 30.0},
    {"pattern": [5, 5, 5], "name": "大当り (STAR)", "score": 0, "denominator": 25.0},
    {"pattern": [4, 4, 4], "name": "ベル", "score": 0, "denominator": 20.0},
    {"pattern": [3, 3, 3], "name": "スイカ", "score": 0, "denominator": 15.0},
    {"pattern": [2, 2, 2], "name": "レモン", "score": 0, "denominator": 12.0},
    {"pattern": [1, 1, 1], "name": "チェリー", "score": 0, "denominator": 10.0},
    {"pattern": [1, 1, "ANY"], "name": "ミニチェリー", "score": 0, "denominator": 7.0},
]

DEFAULT_SLOT_NAME = "標準スロット"



def spin_reels(symbol_data: list[dict[str, Any]], count: int = 3) -> list[dict[str, Any]]:
    """
    リールを回転させ、重みに基づいてランダムな出目を取得します。
    """
    if not symbol_data:
        return []

    weights = [s.get("weight", 1.0) for s in symbol_data]
    return random.choices(symbol_data, weights=weights, k=count)


def evaluate_slot_spin(result: list[dict[str, Any]], payouts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    出目を判定し、成立した役を返します。
    """
    if not result:
        return None

    result_ids = [s["id"] for s in result]

    for payout in payouts:
        pattern = payout["pattern"]
        if len(pattern) != len(result_ids):
            continue

        match = True
        for i in range(len(pattern)):
            if pattern[i] == "ANY":
                continue
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
        return migrate_slot_config({"name": DEFAULT_SLOT_NAME, "symbols": DEFAULT_SYMBOLS, "payouts": DEFAULT_PAYOUTS})

    return migrate_slot_config(storage_data)


def migrate_slot_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    設定データを最新形式（IDベース、分母対応）に変換・補完します。
    """
    name = config.get("name", DEFAULT_SLOT_NAME)
    symbols = config.get("symbols", DEFAULT_SYMBOLS)
    payouts = config.get("payouts", DEFAULT_PAYOUTS)

    # 1. シンボルの移行
    new_symbols = []
    for i, s in enumerate(symbols):
        new_s = s.copy()
        if "id" not in new_s:
            new_s["id"] = i + 1
        if "image_url" not in new_s:
            new_s["image_url"] = None
        if "weight" not in new_s:
            new_s["weight"] = 1.0
        new_symbols.append(new_s)

    # 2. 役パターンの移行
    char_to_id = {s["char"]: s["id"] for s in new_symbols}
    new_payouts = []
    for p in payouts:
        new_p = p.copy()
        old_pattern = p.get("pattern", [])
        new_pattern = []
        for item in old_pattern:
            if isinstance(item, str) and item in char_to_id:
                new_pattern.append(char_to_id[item])
            else:
                new_pattern.append(item)
        new_p["pattern"] = new_pattern

        # 分母（denominator）が欠落している場合の計算
        if "denominator" not in new_p:
            new_p["denominator"] = 0.0  # 後で確率計算時に補完

        new_payouts.append(new_p)

    return {
        "name": name,
        "symbols": new_symbols,
        "payouts": new_payouts,
    }


def resolve_pattern_to_chars(pattern: list[Any], symbols: list[dict[str, Any]]) -> list[str]:
    """
    IDベースのパターンを表示用の文字リストに変換します。
    """
    id_to_char = {s["id"]: s["char"] for s in symbols}
    return [id_to_char.get(item, str(item)) if item != "ANY" else "ANY" for item in pattern]


def calculate_probabilities(symbol_data: list[dict[str, Any]], payouts: list[dict[str, Any]]) -> dict[str, Any]:
    """
    現在の設定に基づき、各役の成立確率(1/N)とハズレ確率を計算します。
    """
    if not symbol_data:
        return {"hit_rates": [], "total_hit_rate": 0.0, "miss_rate": 100.0}

    total_weight = sum(s["weight"] for s in symbol_data)
    if total_weight == 0:
        return {"hit_rates": [], "total_hit_rate": 0.0, "miss_rate": 100.0}

    results = []
    total_hit_prob = 0.0

    # 総当たり計算（3リール固定）
    if len(symbol_data) <= 15:
        pattern_counts: dict[str, float] = {p["name"]: 0.0 for p in payouts}

        for s1 in symbol_data:
            p1 = s1["weight"] / total_weight
            for s2 in symbol_data:
                p2 = s2["weight"] / total_weight
                for s3 in symbol_data:
                    p3 = s3["weight"] / total_weight
                    prob = p1 * p2 * p3
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
    else:
        # 近似計算（独立試行として扱う）
        id_probs = {s["id"]: s["weight"] / total_weight for s in symbol_data}
        for p in payouts:
            prob = 1.0
            for item in p["pattern"]:
                if item == "ANY":
                    prob *= 1.0
                else:
                    prob *= id_probs.get(item, 0.0)

            total_hit_prob += prob

    # 各役の分母 (1/N) を算出
    for p in payouts:
        # pattern_counts がある場合はそれを使用、なければ近似値
        if len(symbol_data) <= 15:
            prob = pattern_counts.get(p["name"], 0.0)
        else:
            prob = 1.0
            id_probs = {s["id"]: s["weight"] / total_weight for s in symbol_data}
            for item in p["pattern"]:
                prob *= 1.0 if item == "ANY" else id_probs.get(item, 0.0)

        denominator = round(1.0 / prob, 1) if prob > 0 else 0.0
        results.append({"name": p["name"], "rate": prob * 100, "denominator": denominator})

    return {
        "hit_rates": results,
        "total_hit_rate": total_hit_prob * 100,
        "miss_rate": max(0.0, (1.0 - total_hit_prob) * 100),
    }


def solve_weights_from_denominators(
    symbol_data: list[dict[str, Any]],
    payouts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    役の分母(1/N)から図柄の重みを逆算して更新します。
    パチスロ風の簡易逆算ロジック。
    """
    if not symbol_data or not payouts:
        return symbol_data

    # 各図柄が必要とされる累積確率（1リールあたり）
    required_probs: dict[int, float] = {s["id"]: 0.0 for s in symbol_data}

    for p in payouts:
        denom = p.get("denominator", 0.0)
        if denom <= 0:
            continue

        target_prob = 1.0 / denom
        pattern = p["pattern"]

        # 簡易化: ANYを除いた図柄が均等に寄与すると仮定
        active_slots = [i for i, item in enumerate(pattern) if item != "ANY"]
        if not active_slots:
            continue

        # 1つの図柄あたりの必要確率 p = target_prob ^ (1/出現回数)
        # 例: 1/7.3 のリプレイ (4,4,4) なら p = (1/7.3)^(1/3) ≒ 0.51
        # 例: 1/40 のチェリー (1, ANY, ANY) なら p = (1/40)^(1/1) = 0.025

        # 実際には複数役で同じ図柄を使うため、最大値を採用
        unique_ids = set([pattern[i] for i in active_slots])
        for sym_id in unique_ids:
            count = pattern.count(sym_id)
            p_val = target_prob ** (1.0 / count)
            required_probs[sym_id] = max(required_probs[sym_id], p_val)

    # 合計確率が1.0を超えないようにスケーリング（ハズレ分を確保）
    total_req = sum(required_probs.values())
    max_allowed = 0.95  # 5%はハズレ用に空ける

    if total_req > max_allowed:
        scale = max_allowed / total_req
        for sym_id in required_probs:
            required_probs[sym_id] *= scale
        total_req = max_allowed

    # 残りの確率を未割り当ての図柄または全図柄に均等配分
    remaining = 1.0 - total_req

    # 役に使われていない図柄（ハズレ図柄）を特定
    used_ids = set()
    for p in payouts:
        for item in p["pattern"]:
            if item != "ANY":
                used_ids.add(item)

    unused_symbols = [s["id"] for s in symbol_data if s["id"] not in used_ids]

    if unused_symbols and remaining > 0:
        # ハズレ専用図柄がある場合はそこに全配分
        p_extra = remaining / len(unused_symbols)
        for sym_id in unused_symbols:
            required_probs[sym_id] += p_extra
    else:
        # すべてが役図柄の場合は、現状の比率を維持して配分（簡易的に全配分）
        p_extra = remaining / len(symbol_data)
        for sym_id in required_probs:
            required_probs[sym_id] += p_extra

    new_symbol_data = []
    for s in symbol_data:
        new_s = s.copy()
        # 重みを 1000倍して整数に近くする
        new_s["weight"] = max(0.1, round(required_probs[s["id"]] * 1000, 1))
        new_symbol_data.append(new_s)

    return new_symbol_data


def validate_slot_config(config: dict[str, Any]) -> tuple[bool, str]:
    """
    設定データの整合性をチェックします。
    """
    if not config.get("name"):
        return False, "スロットの名前がありません。"

    symbols = config.get("symbols", [])
    if not symbols:
        return False, "図柄が一つも登録されていません。"

    ids = [s.get("id") for s in symbols if "id" in s]
    if len(ids) != len(set(ids)):
        return False, "図柄のIDが重複しています。"

    payouts = config.get("payouts", [])
    if not payouts:
        return False, "役が一つも登録されていません。"

    valid_ids = set(ids)
    for p in payouts:
        if not p.get("name"):
            return False, "役名が空の項目があります。"
        pattern = p.get("pattern", [])
        if len(pattern) != 3:
            return False, f"役「{p['name']}」のパターンが3リール分設定されていません。"
        for item in pattern:
            if item != "ANY" and item not in valid_ids:
                return False, f"役「{p['name']}」に存在しない図柄ID({item})が使われています。"

    return True, ""
