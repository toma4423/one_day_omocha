import pytest
from unittest.mock import MagicMock
import streamlit as st
import json
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
    
    # Initialize session state
    st.session_state["csb_test_1"] = 10
    st.session_state["csb_test_2"] = 20
    st.session_state["other_test"] = 30
    
    # Execute clear
    safe_storage.clear_all_with_prefix("csb_")
    
    # Verify session state removal
    assert "csb_test_1" not in st.session_state
    assert "csb_test_2" not in st.session_state
    assert "other_test" in st.session_state
    
    # Verify storage deletion calls
    calls = [call.args[0] for call in mock_storage.deleteItem.call_args_list]
    assert "csb_test_1" in calls
    assert "csb_test_2" in calls

def test_safe_storage_json_serialization():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    
    complex_data = {"rows": 5, "cells": {"0_0": {"count": 1}}}
    safe_storage.set_item("json_key", complex_data)
    
    # Verify that it was serialized to JSON string
    called_args = mock_storage.setItem.call_args[0]
    assert called_args[0] == "json_key"
    assert json.loads(called_args[1]) == complex_data

def test_safe_storage_get_item_with_json():
    mock_storage = MagicMock()
    complex_data = {"val": 123}
    mock_storage.getItem.return_value = json.dumps(complex_data)
    
    safe_storage = SafeStorage(mock_storage)
    result = safe_storage.get_item("json_key", is_json=True)
    assert result == complex_data

def test_safe_storage_get_item_returns_none_on_failure():
    mock_storage = MagicMock()
    mock_storage.getItem.side_effect = Exception("Fail")
    safe_storage = SafeStorage(mock_storage)
    assert safe_storage.get_item("any") is None
