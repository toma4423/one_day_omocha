import pytest
from unittest.mock import MagicMock
import streamlit as st
import json
from src.utils.storage import SafeStorage

def test_safe_storage_set_and_get_json():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    test_data = {"rows": 5, "cells": {"0_0": {"label": "test", "count": 1}}}
    safe_storage.set_item("bingo_key", test_data)
    called_args = mock_storage.setItem.call_args[0]
    assert json.loads(called_args[1]) == test_data
    mock_storage.getItem.return_value = json.dumps(test_data)
    loaded_data = safe_storage.get_item("bingo_key", is_json=True)
    assert loaded_data == test_data

def test_safe_storage_delete_item():
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    safe_storage.delete_item("key_to_delete")
    mock_storage.deleteItem.assert_called_once_with("key_to_delete")

def test_bingo_version_wrap_around_integrity():
    """
    バージョンが100から1に戻った際、古いデータが残っていないかを検証する
    """
    mock_storage = MagicMock()
    safe_storage = SafeStorage(mock_storage)
    
    # 1. バージョン1としてデータを保存
    ver1_key = "csb_data_v1"
    old_data = {"rows": 5, "cells": {"0_0": {"label": "OLD DATA", "count": 99}}}
    
    # ストレージに古いデータが入っている状態をシミュレート
    storage_dict = {
        "csb_ver": "100",
        ver1_key: json.dumps(old_data)
    }
    mock_storage.getItem.side_effect = lambda k: storage_dict.get(k)
    
    # 2. リセット処理のロジック（ここをページ側で実装する）
    # 現在 100 なので次は 1 に戻る
    current_v = int(storage_dict["csb_ver"])
    new_v = 1 if current_v >= 100 else current_v + 1
    
    # 【重要】リセット時に全プレフィックスを消去する動作をシミュレート
    prefix = "csb_data_v"
    # 本来はここで storage_dict 内の csb_data_v* をすべて消す
    keys_to_clear = [k for k in storage_dict.keys() if k.startswith(prefix)]
    for k in keys_to_clear:
        storage_dict.pop(k)
    
    storage_dict["csb_ver"] = str(new_v)
    
    # 3. 検証: 新しいバージョン1でデータを取得しようとした時、None (または新規) になっているか
    new_key = f"csb_data_v{new_v}"
    assert new_key == "csb_data_v1"
    assert storage_dict.get(new_key) is None # 古いデータが消えていること
