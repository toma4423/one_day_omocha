import streamlit as st
import json
from typing import Any, Optional

class SafeStorage:
    """
    Streamlit の LocalStorage 操作を安全に行うためのクラスです。
    """
    def __init__(self, storage_instance):
        self.storage = storage_instance

    def set_item(self, key: str, value: Any):
        """値を JSON 文字列として確実に保存します。"""
        try:
            # 常に JSON 文字列にして保存することで型の不整合を防ぐ
            json_val = json.dumps(value, ensure_ascii=False)
            self.storage.setItem(key, json_val)
        except Exception:
            pass

    def get_item(self, key: str, is_json: bool = True) -> Optional[Any]:
        """保存された JSON 文字列をパースして取得します。"""
        try:
            val = self.storage.getItem(key)
            if val is None or val == "null" or val == "":
                return None
            if is_json:
                # すでに辞書やリストの場合はそのまま返し、文字列の場合はパースする
                if isinstance(val, (dict, list)):
                    return val
                return json.loads(val)
            return val
        except Exception:
            return None

    def delete_item(self, key: str):
        try:
            self.storage.deleteItem(key)
        except Exception:
            pass

    def clear_all_with_prefix(self, prefix: str):
        """指定したプレフィックスを持つアイテムを削除"""
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
            self.delete_item(key)
