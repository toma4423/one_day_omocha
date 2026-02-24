def calculate_new_position(current_pos: int, dice_sum: int, total_tiles: int, is_loop: bool) -> int:
    """
    サイコロの出目に基づき、新しいコマの位置を計算します。
    """
    new_pos = current_pos + dice_sum

    if is_loop:
        # 循環型：マスの数で割った余り
        return new_pos % total_tiles
    else:
        # 直線型：最大値（ゴール）で止まる
        if new_pos >= total_tiles:
            return total_tiles - 1
        return new_pos


def init_board_data(total_tiles: int, board_type: str) -> dict[str, str]:
    """
    盤面の初期データを生成します。
    """
    board_data = {}
    for i in range(total_tiles):
        key = f"sg_tile_{i}"
        if board_type == "スタートからゴール":
            if i == 0:
                board_data[key] = "🚩 START"
            elif i == total_tiles - 1:
                board_data[key] = "🏆 GOAL"
            else:
                board_data[key] = f"マス {i + 1}"
        else:
            board_data[key] = f"マス {i + 1}"
    return board_data
