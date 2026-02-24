import pytest
from unittest.mock import MagicMock, patch
import json
from src.utils.storage import SafeStorage

def test_safe_storage_set_and_get_json(mock_storage):
    safe_storage = SafeStorage(mock_storage)
    test_data = {"key": "value", "num": 123}
    
    # set_item
    safe_storage.set_item("test_key", test_data)
    mock_storage.setItem.assert_called_once()
    args = mock_storage.setItem.call_args[0]
    assert args[0] == "test_key"
    assert json.loads(args[1]) == test_data

    # get_item (JSON)
    mock_storage.getItem.return_value = json.dumps(test_data)
    assert safe_storage.get_item("test_key", is_json=True) == test_data

def test_safe_storage_error_handling(mock_storage):
    safe_storage = SafeStorage(mock_storage)
    
    # 壊れたJSONの取得
    mock_storage.getItem.return_value = "{ invalid json }"
    assert safe_storage.get_item("bad_key") is None
    
    # setItemの例外発生
    mock_storage.setItem.side_effect = Exception("Storage full")
    # 例外が内部でキャッチされ、クラッシュしないことを確認
    safe_storage.set_item("any_key", {"data": 1})

def test_safe_storage_get_item_variations(mock_storage):
    safe_storage = SafeStorage(mock_storage)
    
    cases = [
        (None, None),
        ("null", None),
        ("", None),
        ("just a string", "just a string"),
    ]
    
    for input_val, expected in cases:
        mock_storage.getItem.return_value = input_val
        assert safe_storage.get_item("key", is_json=False) == expected

def test_safe_storage_clear_all_with_prefix(mock_storage):
    safe_storage = SafeStorage(mock_storage)
    session_state = {
        "target_1": "v1",
        "target_2": "v2",
        "keep_me": "v3"
    }
    
    safe_storage.clear_all_with_prefix("target_", session_state)
    
    # session_stateから消えていること
    assert "target_1" not in session_state
    assert "target_2" not in session_state
    assert "keep_me" in session_state
    
    # LocalStorageからも消えていること
    assert mock_storage.deleteItem.call_count == 2

