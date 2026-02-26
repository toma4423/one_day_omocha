def calculate_total_points(daily_points: list[int]) -> int:
    """日ごとのポイント合計を計算します。"""
    return sum(daily_points)


def evaluate_rank_status(total_points: int) -> str:
    """現在の合計ポイントからランクのステータスを評価します。"""
    if total_points >= 18:
        return "ランクアップ"
    elif total_points >= 12:
        return "キープ"
    else:
        return "ランクダウン"


def points_needed_for_keep(total_points: int) -> int:
    """キープ（12ポイント）までに必要なポイントを計算します。"""
    return max(0, 12 - total_points)


def points_needed_for_rank_up(total_points: int) -> int:
    """ランクアップ（18ポイント）までに必要なポイントを計算します。"""
    return max(0, 18 - total_points)
