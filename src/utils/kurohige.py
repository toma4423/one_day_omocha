import random


def init_kurohige(num_slots: int) -> int:
    """
    当たり（爆発）のインデックスをランダムに決定します。
    """
    if num_slots <= 0:
        raise ValueError("穴の数は1以上に設定してください。")
    return random.randint(0, num_slots - 1)

def check_slot(idx: int, target: int) -> str:
    """
    指定されたインデックスが当たりかどうかを判定します。
    """
    if idx == target:
        return "boom"
    return "safe"

def is_already_clicked(idx: int, clicked_list: list[int]) -> bool:
    """
    すでにクリックされたインデックスかどうかを確認します。
    """
    return idx in clicked_list
