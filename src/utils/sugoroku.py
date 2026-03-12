from pydantic import BaseModel, Field


class SugorokuTile(BaseModel):
    """双六の各マスを定義するモデル"""

    id: int
    text: str = ""
    effect: str | None = None  # 将来的な拡張用


class SugorokuBoard(BaseModel):
    """双六の盤面全体を定義するモデル"""

    total_tiles: int = Field(default=20, ge=5, le=100)
    is_loop: bool = False
    tiles: list[SugorokuTile] = []


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


def create_board(total_tiles: int, is_loop: bool, board_type: str = "スタートからゴール") -> SugorokuBoard:
    """
    盤面を生成します。
    """
    tiles = []
    for i in range(total_tiles):
        text = f"マス {i + 1}"
        if not is_loop:
            if i == 0:
                text = "🚩 START"
            elif i == total_tiles - 1:
                text = "🏆 GOAL"

        tiles.append(SugorokuTile(id=i, text=text))

    return SugorokuBoard(total_tiles=total_tiles, is_loop=is_loop, tiles=tiles)
