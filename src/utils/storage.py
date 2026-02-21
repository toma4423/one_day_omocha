import streamlit as st
from streamlit_local_storage import LocalStorage

def get_storage():
    """
    LocalStorage のインスタンスを返します。
    """
    return LocalStorage()

def sync_state_to_storage(prefix: str, keys: list[str]):
    """
    セッション状態にある指定されたキーを LocalStorage に保存します。
    """
    storage = get_storage()
    for key in keys:
        if key in st.session_state:
            val = st.session_state[key]
            storage.setItem(f"{prefix}_{key}", val)

def load_state_from_storage(prefix: str, keys: list[str]):
    """
    LocalStorage から指定されたキーの値を読み込み、セッション状態にセットします。
    """
    storage = get_cell_storage() # 既存のLocal Storageから値を取得
    # streamlit_local_storage は非同期的な動作をすることがあるため、
    # 実際の実装ではコンポーネントの返り値を監視する必要があります。
    pass
