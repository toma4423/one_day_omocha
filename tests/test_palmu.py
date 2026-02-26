from datetime import date

from src.utils.palmu import (
    calculate_skip_card_balance,
    calculate_total_points,
    evaluate_rank_status,
    generate_point_presets,
    group_points_by_active_week,
    points_needed_for_keep,
    points_needed_for_rank_up,
)


def test_calculate_total_points():
    assert calculate_total_points([6, 4, 2, 0, 0, 0, 0]) == 12
    assert calculate_total_points([1, 1, 1, 1, 1, 1, 1]) == 7
    assert calculate_total_points(["スキップ", 4, 2, 0, 0, 0, 0]) == 6
    assert calculate_total_points([6, "スキップ", "スキップ", 1]) == 7
    assert calculate_total_points([]) == 0


def test_evaluate_rank_status():
    assert evaluate_rank_status(18) == "ランクアップ"
    assert evaluate_rank_status(20) == "ランクアップ"
    assert evaluate_rank_status(12) == "キープ"
    assert evaluate_rank_status(17) == "キープ"
    assert evaluate_rank_status(11) == "ランクダウン"
    assert evaluate_rank_status(0) == "ランクダウン"


def test_points_needed_for_keep():
    assert points_needed_for_keep(0) == 12
    assert points_needed_for_keep(10) == 2
    assert points_needed_for_keep(12) == 0
    assert points_needed_for_keep(15) == 0


def test_points_needed_for_rank_up():
    assert points_needed_for_rank_up(0) == 18
    assert points_needed_for_rank_up(12) == 6
    assert points_needed_for_rank_up(18) == 0
    assert points_needed_for_rank_up(20) == 0


def test_generate_point_presets():
    presets_18 = generate_point_presets(18)
    assert len(presets_18) > 0
    for p in presets_18:
        assert len(p) == 7
        assert sum(p) >= 18

    presets_12 = generate_point_presets(12)
    assert len(presets_12) > 0
    for p in presets_12:
        assert len(p) == 7
        assert sum(p) >= 12


def test_calculate_skip_card_balance():
    # 2/23(月) 開始とする
    start = date(2026, 2, 23)
    daily = [1, "スキップ", 1, 1, 1, 1, 1, 1, 1]  # 9日間
    # 初日(月)に+2、翌日(火)にスキップで-1
    balances = calculate_skip_card_balance(2, start, 9, daily)
    assert balances[0] == 4  # 2+2
    assert balances[1] == 3  # 4-1
    assert balances[2] == 3
    # 2週目月曜日(3/2)にさらに+2 (上限10)
    start2 = date(2026, 3, 1)  # 日曜日開始
    daily2 = [1, 1, 1]  # 日月火
    balances2 = calculate_skip_card_balance(9, start2, 3, daily2)
    assert balances2[0] == 9  # 日
    assert balances2[1] == 10  # 月 (9+2=11 -> 10)
    assert balances2[2] == 10  # 火


def test_group_points_by_active_week():
    daily = [6, 4, "スキップ", 4, 1, 1, 1, 1, 2, 2]
    # スキップ除外: [6, 4, 4, 1, 1, 1, 1, 2, 2]
    # 7日ごと: [[6, 4, 4, 1, 1, 1, 1], [2, 2]]
    weeks = group_points_by_active_week(daily)
    assert len(weeks) == 2
    assert sum(weeks[0]) == 18
    assert sum(weeks[1]) == 4
