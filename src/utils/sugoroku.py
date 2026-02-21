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
