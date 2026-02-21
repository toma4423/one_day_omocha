import streamlit as st
from typing import Any, Optional

class SafeStorage:
    """
    Streamlit の LocalStorage 操作を安全に行うためのクラスです。
    """
    def __init__(self, storage_instance):
        self.storage = storage_instance

    def set_item(self, key: str, value: Any):
        try:
            self.storage.setItem(key, value)
        except Exception:
            pass

    def get_item(self, key: str) -> Optional[Any]:
        try:
            return self.storage.getItem(key)
        except Exception:
            return None

    def delete_item(self, key: str):
        try:
            self.storage.deleteItem(key)
        except Exception:
            pass

    def clear_all_with_prefix(self, prefix: str):
        """指定したプレフィックスを持つアイテムをセッションとLocalStorageから削除"""
        # セッション状態から削除
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
            # LocalStorage からも削除
            self.delete_item(key)
