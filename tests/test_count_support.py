from src.utils.count_support import calculate_diff_xy, calculate_final_score, calculate_weighted_value


def test_calculate_weighted_value():
    assert calculate_weighted_value(10, 1.5) == 15.0
    assert calculate_weighted_value(7, 0.3) == 2.1


def test_calculate_diff_xy():
    assert calculate_diff_xy(100, 30) == 70.0
    assert calculate_diff_xy(50, 120) == -70.0


def test_calculate_final_score():
    assert calculate_final_score(100, 20, 10) == 70.0
    assert calculate_final_score(50, 60, 10) == -20.0
