def mock_get_current_version(v_raw, v_store):
    """
    pages/21_...py の get_current_version ロジックの模擬
    """
    if v_raw:
        v_str = str(v_raw)
        if v_str.isdigit():
            return v_str
    if v_store and str(v_store).isdigit():
        return str(v_store)
    return "1"


def test_get_current_version_robustness():
    # 正常系
    assert mock_get_current_version("10", None) == "10"
    assert mock_get_current_version(None, "20") == "20"

    # 異常系：文字列混入
    assert mock_get_current_version("abc", None) == "1"
    assert mock_get_current_version(None, "xyz") == "1"

    # 異常系：リスト形式（古いStreamlitの挙動など）
    assert mock_get_current_version(["5"], None) == "1"

    # 異常系：空文字
    assert mock_get_current_version("", "") == "1"


def test_reset_logic_robustness():
    # 実際のコードで行っている try-except の模擬
    def safe_int_convert(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return 1

    assert safe_int_convert("10") == 10
    assert safe_int_convert("not_a_number") == 1
    assert safe_int_convert(None) == 1
