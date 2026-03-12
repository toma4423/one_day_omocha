import random
from typing import Any, Literal

from pydantic import BaseModel


class SlotSymbol(BaseModel):
    """スロットの図柄を定義するモデル"""

    id: int
    char: str
    weight: float = 1.0
    image_url: str | None = None


class SlotPayout(BaseModel):
    """スロットの役（払い出し）を定義するモデル"""

    pattern: list[int | Literal["ANY"]]
    name: str
    score: int = 0
    denominator: float = 0.0


class SlotConfig(BaseModel):
    """スロット全体の設定を管理するモデル"""

    name: str = "標準スロット"
    symbols: list[SlotSymbol]
    payouts: list[SlotPayout]


# デフォルト設定 (Pydanticモデル化)
DEFAULT_SYMBOLS = [
    SlotSymbol(id=1, char="🍒", weight=15.0),
    SlotSymbol(id=2, char="🍋", weight=10.0),
    SlotSymbol(id=3, char="🍉", weight=7.0),
    SlotSymbol(id=4, char="🔔", weight=5.0),
    SlotSymbol(id=5, char="⭐", weight=3.0),
    SlotSymbol(id=6, char="7️⃣", weight=2.0),
]

DEFAULT_PAYOUTS = [
    SlotPayout(pattern=[6, 6, 6], name="超大当り (777)", denominator=30.0),
    SlotPayout(pattern=[5, 5, 5], name="大当り (STAR)", denominator=25.0),
    SlotPayout(pattern=[4, 4, 4], name="ベル", denominator=20.0),
    SlotPayout(pattern=[3, 3, 3], name="スイカ", denominator=15.0),
    SlotPayout(pattern=[2, 2, 2], name="レモン", denominator=12.0),
    SlotPayout(pattern=[1, 1, 1], name="チェリー", denominator=10.0),
    SlotPayout(pattern=[1, 1, "ANY"], name="ミニチェリー", denominator=7.0),
]


def spin_reels(config: SlotConfig, count: int = 3) -> list[SlotSymbol]:
    """
    パチスロ式の内部抽選を行い、出目を決定します。
    """
    # 1. 内部抽選（フラグ抽選）
    sorted_payouts = sorted(config.payouts, key=lambda x: x.denominator, reverse=True)

    winning_payout = None
    for p in sorted_payouts:
        if p.denominator > 0:
            if random.random() < (1.0 / p.denominator):
                winning_payout = p
                break

    # 2. 出目の決定
    if winning_payout:
        result = []
        for item in winning_payout.pattern:
            if item == "ANY":
                result.append(random.choice(config.symbols))
            else:
                symbol = next((s for s in config.symbols if s.id == item), config.symbols[0])
                result.append(symbol)
        return result
    else:
        # ハズレ：役が揃わないようにする
        for _ in range(10):
            weights = [s.weight for s in config.symbols]
            result = random.choices(config.symbols, weights=weights, k=count)
            if not evaluate_slot_spin(result, config.payouts):
                return result
        return result


def evaluate_slot_spin(result: list[SlotSymbol], payouts: list[SlotPayout]) -> SlotPayout | None:
    """
    出目を判定し、成立した役を返します。
    """
    if not result:
        return None

    result_ids = [s.id for s in result]
    sorted_payouts = sorted(payouts, key=lambda x: x.denominator, reverse=True)

    for payout in sorted_payouts:
        pattern = payout.pattern
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


def get_slot_config(storage_data: dict[str, Any] | None) -> SlotConfig:
    """
    ストレージデータから設定を取得、またはデフォルトを返します。
    """
    if not storage_data:
        return SlotConfig(symbols=DEFAULT_SYMBOLS, payouts=DEFAULT_PAYOUTS)

    # データのマイグレーションとモデル変換
    try:
        return SlotConfig(**storage_data)
    except Exception:
        # 構造が古い場合はデフォルトを返すか、個別に補完する
        return SlotConfig(symbols=DEFAULT_SYMBOLS, payouts=DEFAULT_PAYOUTS)


def calculate_probabilities(config: SlotConfig) -> dict[str, Any]:
    """
    内部抽選方式に基づき、各役の成立確率を表示用にまとめます。
    """
    results = []
    total_hit_prob = 0.0

    for p in config.payouts:
        prob = (1.0 / p.denominator) if p.denominator > 0 else 0.0
        total_hit_prob += prob
        results.append({"name": p.name, "rate": prob * 100, "denominator": p.denominator})

    return {
        "hit_rates": results,
        "total_hit_rate": min(100.0, total_hit_prob * 100),
        "miss_rate": max(0.0, (1.0 - total_hit_prob) * 100),
    }


def validate_slot_config(config_dict: dict[str, Any]) -> tuple[bool, str]:
    """
    設定データの整合性をチェックします。
    """
    try:
        config = SlotConfig(**config_dict)
    except Exception as e:
        return False, f"設定データの形式が正しくありません: {e}"

    if not config.symbols:
        return False, "図柄が一つも登録されていません。"

    ids = [s.id for s in config.symbols]
    if len(ids) != len(set(ids)):
        return False, "図柄のIDが重複しています。"

    if not config.payouts:
        return False, "役が一つも登録されていません。"

    valid_ids = set(ids)
    for p in config.payouts:
        if len(p.pattern) != 3:
            return False, f"役「{p.name}」のパターンが3リール分設定されていません。"
        for item in p.pattern:
            if item != "ANY" and item not in valid_ids:
                return False, f"役「{p.name}」に存在しない図柄ID({item})が使われています。"

    return True, ""
