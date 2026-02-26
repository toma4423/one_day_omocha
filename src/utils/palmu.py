def calculate_total_points(daily_points: list[int | str]) -> int:
    """日ごとのポイント合計を計算します（'スキップ'等は0として扱う）。"""
    return sum(int(p) for p in daily_points if isinstance(p, int) or (isinstance(p, str) and p.isdigit()))


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


def generate_point_presets(target: int) -> list[tuple[int, ...]]:
    """目標ポイント（12または18）を達成するための7日間のポイント構成例を生成します。"""
    options = [6, 4, 2, 1, 0]
    results = []

    def backtrack(current_combination: list[int], current_sum: int, start_idx: int) -> None:
        if len(current_combination) == 7:
            if current_sum >= target:
                results.append(tuple(current_combination))
            return

        for i in range(start_idx, len(options)):
            # 枝刈り：残りのすべてを最大値(6)にしても目標に届かない場合はスキップ
            if current_sum + options[i] + 6 * (7 - len(current_combination) - 1) < target:
                continue

            current_combination.append(options[i])
            backtrack(current_combination, current_sum + options[i], i)
            current_combination.pop()

    backtrack([], 0, 0)

    # ピッタリのものを優先し、合計値でソート、その後高得点日の少なさでソート
    results.sort(key=lambda x: (sum(x), x.count(6), x.count(4), -x.count(1)))

    # 代表的なものをいくつかピックアップして返す
    # ユーザーが求めていた [6, 4, 4, 1, 1, 1, 1] などの直感的なものを優先
    # 少しフィルタリングして多様な選択肢を5つ程度返す

    filtered_results: list[tuple[int, ...]] = []
    for r in results:
        # 特徴的な構成を抽出
        if len(filtered_results) < 6:
            filtered_results.append(r)

    # 特定のパターン（ユーザー要望）が含まれていなければ追加
    if target == 18:
        user_req = (6, 4, 4, 1, 1, 1, 1)
        if user_req not in filtered_results:
            filtered_results.insert(0, user_req)
            filtered_results = filtered_results[:6]

    return sorted(list(set(filtered_results)), key=lambda x: (sum(x), x.count(6), x.count(4)), reverse=True)
