from src.utils.kurohige import KurohigeState, init_kurohige_state


def test_kurohige_initialization():
    state = init_kurohige_state(12)
    assert state.num_slots == 12
    assert 0 <= state.target_slot < 12
    assert state.status == "playing"
    assert len(state.clicked_slots) == 0


def test_kurohige_reset():
    state = init_kurohige_state(12)
    state.click_slot(0)
    state.reset(16)
    assert state.num_slots == 16
    assert len(state.clicked_slots) == 0
    assert state.status == "playing"


def test_kurohige_click_safe():
    state = KurohigeState(num_slots=12, target_slot=5)
    state.status = "playing"
    res = state.click_slot(3)
    assert res == "playing"
    assert 3 in state.clicked_slots


def test_kurohige_click_boom():
    state = KurohigeState(num_slots=12, target_slot=5)
    state.status = "playing"
    res = state.click_slot(5)
    assert res == "boom"
    assert state.status == "boom"


def test_kurohige_invalid_click():
    state = KurohigeState(num_slots=12, target_slot=5)
    state.status = "playing"
    state.click_slot(3)
    # 同じところをクリックしても何も起きない
    state.click_slot(3)
    assert len(state.clicked_slots) == 1
