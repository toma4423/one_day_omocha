from src.utils.count_support import (
    calculate_diff_xy,
    calculate_final_score,
    calculate_weighted_value,
)


def test_calculate_weighted_value():
    assert calculate_weighted_value(10, 1.5) == 15.0
    assert calculate_weighted_value(3, 1.1) == 3.3
    assert calculate_weighted_value(0, 5.0) == 0.0


def test_calculate_diff_xy():
    assert calculate_diff_xy(10.5, 5.2) == 5.3
    assert calculate_diff_xy(5.0, 10.0) == -5.0
    assert calculate_diff_xy(0, 0) == 0.0


def test_calculate_final_score():
    assert calculate_final_score(20.0, 5.0, 3.0) == 12.0
    assert calculate_final_score(10.5, 5.5, 5.0) == 0.0
    assert calculate_final_score(5, 10, 2) == -7.0
