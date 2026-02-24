import random
from typing import Any

DICE_EMOJI: dict[int, str] = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

HAND_RANK: dict[str, dict[str, Any]] = {
    "PINZORO": {"name": "ピンゾロ (1-1-1)", "strength": 1000, "description": "最強の役。"},
    "ARASHI_6": {"name": "アラシ (6-6-6)", "strength": 606, "description": "ゾロ目。数字が大きいほど強い。"},
    "ARASHI_5": {"name": "アラシ (5-5-5)", "strength": 605, "description": "ゾロ目。"},
    "ARASHI_4": {"name": "アラシ (4-4-4)", "strength": 604, "description": "ゾロ目。"},
    "ARASHI_3": {"name": "アラシ (3-3-3)", "strength": 603, "description": "ゾロ目。"},
    "ARASHI_2": {"name": "アラシ (2-2-2)", "strength": 602, "description": "ゾロ目。"},
    "SHIGORO": {"name": "シゴロ (4-5-6)", "strength": 500, "description": "4-5-6の連番。非常に強い。"},
    "POINT_6": {"name": "6の目", "strength": 6, "description": "2つのサイコロが揃い、残りが6。"},
    "POINT_5": {"name": "5の目", "strength": 5, "description": "2つのサイコロが揃い、残りが5。"},
    "POINT_4": {"name": "4の目", "strength": 4, "description": "2つのサイコロが揃い、残りが4。"},
    "POINT_3": {"name": "3の目", "strength": 3, "description": "2つのサイコロが揃い、残りが3。"},
    "POINT_2": {"name": "2の目", "strength": 2, "description": "2つのサイコロが揃い、残りが2。"},
    "POINT_1": {"name": "1の目", "strength": 1, "description": "2つのサイコロが揃い、残りが1。"},
    "BUTA": {"name": "ブタ (役なし)", "strength": 0, "description": "役が成立していない状態。"},
    "HIFUMI": {"name": "ヒフミ (1-2-3)", "strength": -100, "description": "最低の役。即負け。"},
}


def roll_dice(count: int = 1, faces: int = 6) -> list[int]:
    """
    指定された数と面のサイコロを振り、結果をリストで返します。
    """
    return [random.randint(1, faces) for _ in range(count)]


def evaluate_hand(dice: list[int]) -> str:
    """
    チンチロリンの役を判定します。
    """
    if len(dice) != 3:
        return "BUTA"

    sorted_dice = sorted(dice)
    d1, d2, d3 = sorted_dice

    # ピンゾロ
    if d1 == 1 and d2 == 1 and d3 == 1:
        return "PINZORO"

    # アラシ
    if d1 == d2 == d3:
        return f"ARASHI_{d1}"

    # シゴロ
    if d1 == 4 and d2 == 5 and d3 == 6:
        return "SHIGORO"

    # ヒフミ
    if d1 == 1 and d2 == 2 and d3 == 3:
        return "HIFUMI"

    # 目（ポイント）
    if d1 == d2:
        return f"POINT_{d3}"
    if d2 == d3:
        return f"POINT_{d1}"

    return "BUTA"
