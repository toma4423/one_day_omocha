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

def test_calculate_monthly_display_days_no_skip():
    # SKIPがない場合、4期(28日間)がそのまま返るはず
    vals = [1] * 40
    assert calculate_monthly_display_days(vals) == 28

def test_calculate_monthly_display_days_with_skip_suppression():
    # 1日でもSKIPがあり、28日を超える場合、3期(21配信日)分に抑えられる。
    # 例：10日目に1日SKIPを入れると、4期完了には29日必要。
    # そのため3期(21配信日)分、つまり22日間（21配信+1SKIP）が返るはず。
    vals = [1] * 9 + ["SKIP"] + [1] * 30
    assert calculate_monthly_display_days(vals) == 22
