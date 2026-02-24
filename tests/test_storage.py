import pytest
from unittest.mock import MagicMock, patch
import json
from src.utils.storage import SafeStorage

def test_safe_storage_set_and_get_json():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    test_data = {"rows": 5, "cells": {"0_0": {"label": "test", "count": 1}}}
    
    # Test set_item
    safe_storage.set_item("bingo_key", test_data)
    mock_storage.setItem.assert_called_once()
    args, _ = mock_storage.setItem.call_args
    assert args[0] == "bingo_key"
    assert json.loads(args[1]) == test_data

    # Test get_item
    mock_storage.getItem.return_value = json.dumps(test_data)
    loaded_data = safe_storage.get_item("bingo_key", is_json=True)
    assert loaded_data == test_data

def test_safe_storage_get_item_variations():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    
    # String value
    mock_storage.getItem.return_value = "hello"
    assert safe_storage.get_item("key", is_json=False) == "hello"
    
    # Null/Empty values
    mock_storage.getItem.return_value = None
    assert safe_storage.get_item("key") is None
    mock_storage.getItem.return_value = "null"
    assert safe_storage.get_item("key") is None
    mock_storage.getItem.return_value = ""
    assert safe_storage.get_item("key") is None

def test_safe_storage_delete_item():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    safe_storage.delete_item("key_to_delete")
    mock_storage.deleteItem.assert_called_once_with("key_to_delete")

@patch("src.utils.storage.st")
def test_safe_storage_clear_all_with_prefix(mock_st):
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    
    # Mock st.session_state
    mock_st.session_state = {
        "prefix_1": "val1",
        "prefix_2": "val2",
        "other": "val3"
    }
    
    safe_storage.clear_all_with_prefix("prefix_")
    
    assert "prefix_1" not in mock_st.session_state
    assert "prefix_2" not in mock_st.session_state
    assert "other" in mock_st.session_state
    
    # Check if deleteItem was called for prefixed keys
    assert mock_storage.deleteItem.call_count == 2
    mock_storage.deleteItem.assert_any_call("prefix_1")
    mock_storage.deleteItem.assert_any_call("prefix_2")
