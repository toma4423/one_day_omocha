import numpy as np
import random
from typing import Tuple, List

def create_board(w: int, h: int, mines: int) -> np.ndarray:
    """
    指定された幅、高さ、爆弾の数でボードを初期化します。
    -1: 爆弾
    0-8: 周囲の爆弾数
    """
    if mines >= w * h:
        raise ValueError("爆弾の数はマスの数より少なく設定してください。")
    if w <= 0 or h <= 0:
        raise ValueError("幅と高さは1以上に設定してください。")

    board = np.zeros((h, w), dtype=int)
    mines_pos = random.sample(range(w * h), mines)
    for p in mines_pos:
        board[p // w, p % w] = -1
    
    # 周囲の爆弾数を計算
    for r in range(h):
        for c in range(w):
            if board[r, c] == -1:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if 0 <= r + dr < h and 0 <= c + dc < w:
                        if board[r + dr, c + dc] == -1:
                            count += 1
            board[r, c] = count
    return board

def reveal_tile(r: int, c: int, w: int, h: int, board: np.ndarray, revealed: np.ndarray, flags: np.ndarray) -> np.ndarray:
    """
    指定された座標のマスを開きます。0の場合は周囲も再帰的に開きます。
    revealedを更新して返します。
    """
    if not (0 <= r < h and 0 <= c < w):
        return revealed
    if revealed[r, c] or flags[r, c]:
        return revealed
    
    revealed[r, c] = True
    
    # 0の場合は周囲も開く
    if board[r, c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                reveal_tile(r + dr, c + dc, w, h, board, revealed, flags)
    return revealed

def is_game_won(board: np.ndarray, revealed: np.ndarray) -> bool:
    """
    爆弾以外のすべてのマスが開かれているか判定します。
    """
    unrevealed_safe = np.sum((board != -1) & (~revealed))
    return unrevealed_safe == 0
