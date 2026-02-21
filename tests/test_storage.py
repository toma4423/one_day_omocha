import pytest
from unittest.mock import MagicMock
import streamlit as st
import json
from src.utils.storage import SafeStorage

def test_safe_storage_set_and_get_json():
    # Mock の準備
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    
    # テストデータ
    test_data = {"rows": 5, "cells": {"0_0": {"label": "test", "count": 1}}}
    
    # 保存
    safe_storage.set_item("bingo_key", test_data)
    
    # Mock の呼び出し確認 (JSON 文字列になっていること)
    called_args = mock_storage.setItem.call_args[0]
    assert called_args[0] == "bingo_key"
    assert json.loads(called_args[1]) == test_data
    
    # 取得
    mock_storage.getItem.return_value = json.dumps(test_data)
    loaded_data = safe_storage.get_item("bingo_key", is_json=True)
    assert loaded_data == test_data

def test_safe_storage_handles_none():
    mock_storage = MagicMock()
    mock_storage.getItem.return_value = None
    safe_storage = SafeStorage(mock_storage)
    
    assert safe_storage.get_item("non_existent", is_json=True) is None

def test_safe_storage_handles_corrupt_json():
    mock_storage = MagicMock()
    mock_storage.getItem.return_value = "{invalid_json}"
    safe_storage = SafeStorage(mock_storage)
    
    # パースエラー時に例外を投げず None を返すこと
    assert safe_storage.get_item("corrupt_key", is_json=True) is None

def test_safe_storage_delete_item():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    
    safe_storage.delete_item("key_to_delete")
    mock_storage.deleteItem.assert_called_once_with("key_to_delete")
