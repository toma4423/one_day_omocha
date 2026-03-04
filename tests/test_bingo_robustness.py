
def mock_get_current_version(v_raw, v_store):
    if v_raw:
        v_str = str(v_raw)
        if v_str.isdigit():
            return v_str
    if v_store and str(v_store).isdigit():
        return str(v_store)
    return "1"

def simulate_reset_count_only(session_state, rows, cols):
    """
    pages/21_...py の count_only リセットロジックの模擬
    """
    for r in range(rows):
        for c in range(cols):
            session_state[f"csb_count_{r}_{c}"] = 0
    return session_state

def test_bingo_reset_count_only_logic():
    # 状態の準備
    rows, cols = 3, 3
    session_state = {
        "csb_rows": rows,
        "csb_cols": cols,
        "csb_label_0_0": "Test1",
        "csb_count_0_0": 5,
        "csb_label_1_1": "Test2",
        "csb_count_1_1": 10,
    }
    
    # 実行
    new_state = simulate_reset_count_only(session_state, rows, cols)
    
    # 検証: カウントは0になっているが、ラベルは残っていること
    assert new_state["csb_count_0_0"] == 0
    assert new_state["csb_count_1_1"] == 0
    assert new_state["csb_label_0_0"] == "Test1"
    assert new_state["csb_label_1_1"] == "Test2"

def test_mock_get_current_version_robustness():
    # 正常系
    assert mock_get_current_version("10", None) == "10"
    assert mock_get_current_version(None, "20") == "20"
    assert mock_get_current_version("abc", None) == "1"

def test_reset_logic_robustness():
    def safe_int_convert(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return 1

    assert safe_int_convert("10") == 10
    assert safe_int_convert("not_a_number") == 1
