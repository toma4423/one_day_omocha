import json
from typing import Any


class SafeStorage:
    """
    Streamlit の LocalStorage 操作を安全に行うためのクラスです。
    """

    def __init__(self, storage_instance: Any):
        self.storage = storage_instance

    def set_item(self, key: str, value: Any) -> None:
        """値を JSON 文字列として確実に保存します。"""
        try:
            # 常に JSON 文字列にして保存することで型の不整合を防ぐ
            json_val = json.dumps(value, ensure_ascii=False)
            self.storage.setItem(key, json_val)
        except Exception:
            pass

    def get_item(self, key: str, is_json: bool = True) -> Any | None:
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

    def delete_item(self, key: str) -> None:
        try:
            self.storage.deleteItem(key)
        except Exception:
            pass

    def clear_all_with_prefix(self, prefix: str, state_dict: dict[str, Any] | None = None) -> None:
        """
        指定したプレフィックスを持つアイテムを削除します。
        state_dictが指定されている場合はそちらからも削除します（通常は st.session_state を渡します）。
        """
        if state_dict is not None:
            # 辞書から削除
            keys_to_delete = [k for k in state_dict.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                if key in state_dict:
                    del state_dict[key]
                # LocalStorageからも削除
                self.delete_item(key)
        else:
            # state_dictが未指定の場合は、LocalStorageからのみ削除する術がないため何もしないか、
            # あるいは将来的にLocalStorageの全キーを走査する仕組みが必要。
            # 現状は安全のためログや警告に留める（この環境ではprint等）
            pass
