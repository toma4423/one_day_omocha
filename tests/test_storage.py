import pytest
from unittest.mock import MagicMock
from src.utils.storage import SafeStorage

def test_safe_storage_delete_item_handles_keyerror():
    # Mock の作成
    mock_storage = MagicMock()
    # deleteItem が KeyError を投げたとしても SafeStorage が吸収することを確認
    mock_storage.deleteItem.side_effect = KeyError("Not Found")
    
    safe_storage = SafeStorage(mock_storage)
    
    # ここでエラーが起きなければ成功
    try:
        safe_storage.delete_item("non_existent_key")
    except KeyError:
        pytest.fail("SafeStorage should catch and handle KeyError from LocalStorage")

def test_safe_storage_get_item_handles_exception():
    mock_storage = MagicMock()
    mock_storage.getItem.side_effect = Exception("Storage Failed")
    
    safe_storage = SafeStorage(mock_storage)
    
    # エラーが起きずに None を返すことを確認
    assert safe_storage.get_item("any_key") is None

def test_safe_storage_set_item_calls_storage():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    
    safe_storage.set_item("test_key", "test_value")
    mock_storage.setItem.assert_called_once_with("test_key", "test_value")
