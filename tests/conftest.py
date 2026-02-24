import pytest
from unittest.mock import MagicMock
import numpy as np

@pytest.fixture
def mock_streamlit_state(monkeypatch):
    """
    Streamlitのsession_stateをモック化します。
    """
    mock_state = {}
    monkeypatch.setattr("streamlit.session_state", mock_state)
    return mock_state

@pytest.fixture
def mock_storage():
    """
    SafeStorageで使用するLocalStorageのモックを生成します。
    """
    storage = MagicMock()
    # デフォルトの振る舞いを設定
    storage.getItem.return_value = None
    return storage
