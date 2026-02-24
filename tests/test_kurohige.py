import pytest

from src.utils.kurohige import check_slot, init_kurohige, is_already_clicked


def test_init_kurohige():
    num_slots = 12
    for _ in range(100):
        target = init_kurohige(num_slots)
        assert 0 <= target < num_slots

def test_init_kurohige_invalid():
    with pytest.raises(ValueError):
        init_kurohige(0)

def test_check_slot():
    target = 5
    assert check_slot(5, target) == "boom"
    assert check_slot(4, target) == "safe"
    assert check_slot(6, target) == "safe"

def test_is_already_clicked():
    clicked_list = [1, 3, 5]
    assert is_already_clicked(1, clicked_list) == True
    assert is_already_clicked(2, clicked_list) == False
    assert is_already_clicked(5, clicked_list) == True
