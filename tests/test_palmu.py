from src.utils.palmu import (
    calculate_total_points,
    evaluate_rank_status,
    generate_point_presets,
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
