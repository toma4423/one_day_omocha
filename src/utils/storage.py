import streamlit as st
from typing import Any, Optional, List

class SafeStorage:
    """
    Streamlit の LocalStorage 操作を安全に行うためのクラスです。
    """
    def __init__(self, storage_instance):
        self.storage = storage_instance

    def set_item(self, key: str, value: Any):
        """
        値を保存します。
        """
        try:
            self.storage.setItem(key, value)
        except Exception as e:
            st.error(f"LocalStorage 保存エラー ({key}): {e}")

    def get_item(self, key: str) -> Optional[Any]:
        """
        値を取得します。
        """
        try:
            return self.storage.getItem(key)
        except Exception:
            return None

    def delete_item(self, key: str):
        """
        値を削除します。存在しない場合の KeyError を吸収します。
        """
        try:
            # streamlit-local-storage の仕様に合わせて安全に削除
            self.storage.deleteItem(key)
        except (KeyError, AttributeError, Exception):
            pass

def sync_all_to_storage(storage: SafeStorage, prefix: str):
    """
    現在のセッション状態から指定したプレフィックスのデータをすべて LocalStorage に同期します。
    """
    for key in st.session_state.keys():
        if key.startswith(prefix):
            storage.set_item(key, st.session_state[key])
