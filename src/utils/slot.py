import random
from typing import List, Dict, Any, Optional

# デフォルト設定
DEFAULT_SYMBOLS = ["🍒", "🍋", "🍉", "🔔", "⭐", "7️⃣"]
DEFAULT_PAYOUTS = [
    {"pattern": ["7️⃣", "7️⃣", "7️⃣"], "name": "超大当り (777)", "score": 1000},
    {"pattern": ["⭐", "⭐", "⭐"], "name": "大当り (STAR)", "score": 500},
    {"pattern": ["🔔", "🔔", "🔔"], "name": "ベル", "score": 100},
    {"pattern": ["🍉", "🍉", "🍉"], "name": "スイカ", "score": 50},
    {"pattern": ["🍋", "🍋", "🍋"], "name": "レモン", "score": 20},
    {"pattern": ["🍒", "🍒", "🍒"], "name": "チェリー", "score": 10},
    {"pattern": ["🍒", "🍒", "ANY"], "name": "ミニチェリー", "score": 2},
]

def spin_reels(symbols: List[str], count: int = 3) -> List[str]:
    """
    リールを回転させ、ランダムな出目を取得します。
    """
    if not symbols:
        return []
    return [random.choice(symbols) for _ in range(count)]

def evaluate_slot_spin(result: List[str], payouts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
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

def get_slot_config(storage_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    ストレージデータから設定を取得、またはデフォルトを返します。
    """
    if not storage_data:
        return {
            "symbols": DEFAULT_SYMBOLS,
            "payouts": DEFAULT_PAYOUTS
        }
    return {
        "symbols": storage_data.get("symbols", DEFAULT_SYMBOLS),
        "payouts": storage_data.get("payouts", DEFAULT_PAYOUTS)
    }
