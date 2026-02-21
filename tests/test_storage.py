import pytest
from unittest.mock import MagicMock
import streamlit as st
from src.utils.storage import SafeStorage

def test_safe_storage_delete_item_handles_keyerror():
    mock_storage = MagicMock()
    mock_storage.deleteItem.side_effect = KeyError("Not Found")
    safe_storage = SafeStorage(mock_storage)
    try:
        safe_storage.delete_item("non_existent_key")
    except KeyError:
        pytest.fail("SafeStorage should catch and handle KeyError from LocalStorage")

def test_safe_storage_clear_all_with_prefix():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    
    # セッション状態をセット
    st.session_state["csb_test_1"] = 10
    st.session_state["other_test"] = 20
    
    # 実行
    safe_storage.clear_all_with_prefix("csb_")
    
    # csb_ で始まるキーが消えていることを確認
    assert "csb_test_1" not in st.session_state
    assert "other_test" in st.session_state
    
    # deleteItem が呼ばれたことを確認
    mock_storage.deleteItem.assert_called_with("csb_test_1")

def test_safe_storage_get_item_handles_exception():
    mock_storage = MagicMock()
    mock_storage.getItem.side_effect = Exception("Storage Failed")
    safe_storage = SafeStorage(mock_storage)
    assert safe_storage.get_item("any_key") is None

def test_safe_storage_set_item_calls_storage():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    safe_storage.set_item("test_key", "test_value")
    mock_storage.setItem.assert_called_once_with("test_key", "test_value")

def test_safe_storage_json_serialization():
    import json
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    
    complex_data = {"a": 1, "b": [1, 2, 3]}
    safe_storage.set_item("json_key", complex_data)
    
    # 内部で json.dumps が呼ばれているか確認
    # mock_storage.setItem.call_args[0][1] が JSON 文字列であることを確認
    called_val = mock_storage.setItem.call_args[0][1]
    assert json.loads(called_val) == complex_data

def test_safe_storage_json_deserialization():
    import json
    mock_storage = MagicMock()
    complex_data = {"rows": 5, "cells": {"0_0": "test"}}
    mock_storage.getItem.return_value = json.dumps(complex_data)
    
    safe_storage = SafeStorage(mock_storage)
    loaded_data = safe_storage.get_item("json_key", is_json=True)
    
    assert loaded_data == complex_data
