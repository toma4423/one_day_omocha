from src.utils.palmu import calculate_monthly_display_days, calculate_weekly_display_days


def test_calculate_weekly_display_days_all_active():
    # 全て配信の場合、7日間表示されるはず
    vals = [1, 1, 1, 1, 1, 1, 1, 1, 1]
    assert calculate_weekly_display_days(vals) == 7

def test_calculate_weekly_display_days_one_skip():
    # 1日SKIPがある場合、8日間表示されるはず
    vals = [1, "SKIP", 1, 1, 1, 1, 1, 1, 1]
    assert calculate_weekly_display_days(vals) == 8

def test_calculate_weekly_display_days_multiple_skips():
    # 3日SKIPがある場合、10日間表示されるはず
    vals = [1, "SKIP", "SKIP", 1, 1, "SKIP", 1, 1, 1, 1, 1]
    assert calculate_weekly_display_days(vals) == 10

def test_calculate_weekly_display_days_at_the_end():
    # 7日目にSKIPを選択した場合、8日目まで表示されるはず
    vals = [1, 1, 1, 1, 1, 1, "SKIP", 1, 1]
    assert calculate_weekly_display_days(vals) == 8

def test_calculate_weekly_display_days_minimum():
    # SKIPがなくても最低7日間は表示
    vals = [1, 1]
    assert calculate_weekly_display_days(vals) == 7

def test_calculate_monthly_display_days_4_periods():
    # 全て配信の場合、28日間表示されるはず (4期 * 7日)
    vals = [1] * 40
    assert calculate_monthly_display_days(vals, target_periods=4) == 28

def test_calculate_monthly_display_days_with_skips():
    # 配信28日を達成するために、途中にSKIPが2日ある場合、合計30日間になるはず
    vals = [1] * 10 + ["SKIP"] + [1] * 10 + ["SKIP"] + [1] * 10
    assert calculate_monthly_display_days(vals, target_periods=4) == 30
