from datetime import date

from src.utils.palmu import (
    calculate_skip_card_balance,
    calculate_total_points,
    evaluate_rank_status,
    generate_point_presets,
    get_day_period_assignments,
    group_points_by_active_week,
    points_needed_for_keep,
    points_needed_for_rank_up,
)


def test_calculate_total_points_detailed():
    # 基本ケース
    assert calculate_total_points([6, 4, 2, 1, 1, 1, 1]) == 16
    # SKIP混在: 6+4+1=11
    assert calculate_total_points(["SKIP", 6, "SKIP", 4, 1]) == 11
    # 文字列の数字
    assert calculate_total_points(["6", "4", 2]) == 12
    # 空リスト
    assert calculate_total_points([]) == 0
    # 0が含まれる場合
    assert calculate_total_points([0, 0, 0]) == 0


def test_evaluate_rank_status_boundaries():
    # ランクダウン境界
    assert evaluate_rank_status(0) == "ランクダウン"
    assert evaluate_rank_status(11) == "ランクダウン"
    # キープ境界
    assert evaluate_rank_status(12) == "キープ"
    assert evaluate_rank_status(17) == "キープ"
    # ランクアップ境界
    assert evaluate_rank_status(18) == "ランクアップ"
    assert evaluate_rank_status(100) == "ランクアップ"


def test_points_needed_calculations():
    # ランクダウン状態から
    assert points_needed_for_keep(10) == 2
    assert points_needed_for_rank_up(10) == 8
    # キープ状態から
    assert points_needed_for_keep(12) == 0
    assert points_needed_for_rank_up(12) == 6
    # ランクアップ状態から
    assert points_needed_for_keep(20) == 0
    assert points_needed_for_rank_up(20) == 0


def test_generate_point_presets_content():
    for target in [12, 18]:
        presets = generate_point_presets(target)
        assert len(presets) > 0
        for p in presets:
            assert len(p) == 7
            assert sum(p) >= target
            # 0が含まれていないことを確認
            assert 0 not in p


def test_calculate_skip_card_balance_complex():
    # 2026/2/23(月) 開始、初期0枚
    start = date(2026, 2, 23)
    # 月曜なので配布されて+2、火曜SKIPで-1
    daily = [1, "SKIP", 1, 1, 1, 1, 1]
    balances = calculate_skip_card_balance(0, start, 7, daily)
    assert balances[0] == 2  # 月
    assert balances[1] == 1  # 火(SKIP消費)
    assert balances[2] == 1  # 水

    # 上限10枚のテスト
    # 日曜日(3/1)に9枚持っている状態で、翌月曜(3/2)に配布されても10枚で止まる
    start_sun = date(2026, 3, 1)
    daily_no_skip = [1, 1]
    balances_limit = calculate_skip_card_balance(9, start_sun, 2, daily_no_skip)
    assert balances_limit[0] == 9  # 日
    assert balances_limit[1] == 10  # 月 (9+2=11 -> 10)

    # 残高0でSKIPした場合(マイナスにならないこと)
    balances_zero = calculate_skip_card_balance(0, date(2026, 2, 24), 1, ["SKIP"])
    assert balances_zero[0] == 0


def test_group_points_by_active_week_extended():
    # 大量のSKIPがある場合
    daily = ["SKIP", "SKIP", 6, "SKIP", 4, 4, 1, 1, 1, 1, "SKIP", 2]
    # 有効日のみ: [6, 4, 4, 1, 1, 1, 1, 2]
    weeks = group_points_by_active_week(daily)
    assert len(weeks) == 2
    assert weeks[0] == [6, 4, 4, 1, 1, 1, 1]
    assert weeks[1] == [2]


def test_get_day_period_assignments_detailed():
    # 7日ごとに期が上がるか
    daily = [1] * 15  # 15日間配信
    assigns = get_day_period_assignments(daily)
    assert assigns[0] == 1
    assert assigns[6] == 1
    assert assigns[7] == 2
    assert assigns[13] == 2
    assert assigns[14] == 3

    # SKIPが混ざる場合
    daily_skip = [1, "SKIP", 1, 1, 1, 1, 1, 1, 1]
    # 有効配信日インデックス: 0, -, 1, 2, 3, 4, 5, 6, 7
    # 割り当て期: 1, 0, 1, 1, 1, 1, 1, 1, 2
    assigns_skip = get_day_period_assignments(daily_skip)
    assert assigns_skip == [1, 0, 1, 1, 1, 1, 1, 1, 2]
