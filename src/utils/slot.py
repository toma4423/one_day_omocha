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

# デフォルトの役設定 (分母の大きい順に判定)
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


def spin_reels(
    symbol_data: list[dict[str, Any]], payouts: list[dict[str, Any]], count: int = 3
) -> list[dict[str, Any]]:
    """
    パチスロ式の内部抽選を行い、出目を決定します。
    """
    # 1. 内部抽選（フラグ抽選）
    # 分母の大きい（珍しい）役から順に抽選
    sorted_payouts = sorted(payouts, key=lambda x: x.get("denominator", 0), reverse=True)

    winning_payout = None
    for p in sorted_payouts:
        denom = p.get("denominator", 0)
        if denom > 0:
            if random.random() < (1.0 / denom):
                winning_payout = p
                break

    # 2. 出目の決定
    if winning_payout:
        # 当選した役のパターンを表示
        pattern = winning_payout["pattern"]
        result = []
        for item in pattern:
            if item == "ANY":
                # ANYの場合は、その役が成立しない図柄をランダムに選ぶ（簡易化のため全図柄から）
                result.append(random.choice(symbol_data))
            else:
                # 指定されたIDの図柄を探す
                symbol = next((s for s in symbol_data if s["id"] == item), symbol_data[0])
                result.append(symbol)
        return result
    else:
        # ハズレ：ランダムに回すが、役が揃わないようにする
        for _ in range(10):  # 最大10回試行（無限ループ防止）
            weights = [s.get("weight", 1.0) for s in symbol_data]
            result = random.choices(symbol_data, weights=weights, k=count)
            if not evaluate_slot_spin(result, payouts):
                return result
        return result


def evaluate_slot_spin(result: list[dict[str, Any]], payouts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    出目を判定し、成立した役を返します。
    珍しい（分母が大きい）役を優先して判定します。
    """
    if not result:
        return None

    result_ids = [s["id"] for s in result]
    # 分母の大きい順にソートして判定
    sorted_payouts = sorted(payouts, key=lambda x: x.get("denominator", 0), reverse=True)

    for payout in sorted_payouts:
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
    設定データを最新形式に変換・補完します。
    """
    name = config.get("name", DEFAULT_SLOT_NAME)
    symbols = config.get("symbols", DEFAULT_SYMBOLS)
    payouts = config.get("payouts", DEFAULT_PAYOUTS)

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

    new_payouts = []
    for p in payouts:
        new_p = p.copy()
        if "denominator" not in new_p:
            new_p["denominator"] = 0.0
        if "score" not in new_p:
            new_p["score"] = 0
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
    内部抽選方式に基づき、各役の成立確率を表示用にまとめます。
    """
    results = []
    total_hit_prob = 0.0

    for p in payouts:
        denom = p.get("denominator", 0)
        prob = (1.0 / denom) if denom > 0 else 0.0
        total_hit_prob += prob
        results.append({"name": p["name"], "rate": prob * 100, "denominator": denom})

    return {
        "hit_rates": results,
        "total_hit_rate": min(100.0, total_hit_prob * 100),
        "miss_rate": max(0.0, (1.0 - total_hit_prob) * 100),
    }


def solve_weights_from_denominators(
    symbol_data: list[dict[str, Any]],
    payouts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    内部抽選方式では重み計算は不要ですが、互換性のために残します。
    （ハズレ時の出目演出用の重みとして機能します）
    """
    return symbol_data


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
