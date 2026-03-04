import random
from typing import Literal

from pydantic import BaseModel, Field


class MinesweeperState(BaseModel):
    """
    マインスイーパーのゲーム状態を管理するモデルです。
    """

    width: int = Field(8, ge=4, le=20)
    height: int = Field(8, ge=4, le=20)
    num_mines: int = Field(10, ge=1)
    # ボードの値 (-1: 爆弾, 0-8: 周囲の爆弾数)
    board: list[list[int]] = Field(default_factory=list)
    # 開かれたマスの状態
    revealed: list[list[bool]] = Field(default_factory=list)
    # フラグの状態
    flags: list[list[bool]] = Field(default_factory=list)
    # ゲームステータス
    status: Literal["ready", "playing", "won", "lost"] = "ready"

    def reset(self, w: int | None = None, h: int | None = None, mines: int | None = None) -> None:
        """
        ボードを初期化し、ゲームをリセットします。
        """
        if w is not None:
            self.width = w
        if h is not None:
            self.height = h
        if mines is not None:
            self.num_mines = mines

        if self.num_mines >= self.width * self.height:
            self.num_mines = (self.width * self.height) // 5

        # ボードの初期化
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flags = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.status = "playing"

        # 爆弾の配置
        mine_positions = random.sample(range(self.width * self.height), self.num_mines)
        for pos in mine_positions:
            r, c = pos // self.width, pos % self.width
            self.board[r][c] = -1

        # 周囲の爆弾数を計算
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] == -1:
                    continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.height and 0 <= nc < self.width:
                            if self.board[nr][nc] == -1:
                                count += 1
                self.board[r][c] = count

    def reveal_tile(self, r: int, c: int) -> str:
        """
        指定されたマスを開きます。
        """
        if self.status != "playing" or self.flags[r][c] or self.revealed[r][c]:
            return self.status

        if self.board[r][c] == -1:
            self.status = "lost"
            # 爆弾をすべて開く
            for i in range(self.height):
                for j in range(self.width):
                    if self.board[i][j] == -1:
                        self.revealed[i][j] = True
            return self.status

        self._flood_fill(r, c)

        # 勝利判定
        if self._check_win():
            self.status = "won"

        return self.status

    def _flood_fill(self, r: int, c: int) -> None:
        """
        再帰的にタイルを開きます（0の場合）。
        """
        if not (0 <= r < self.height and 0 <= c < self.width) or self.revealed[r][c] or self.flags[r][c]:
            return

        self.revealed[r][c] = True

        if self.board[r][c] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self._flood_fill(r + dr, c + dc)

    def toggle_flag(self, r: int, c: int) -> None:
        """
        フラグを切り替えます。
        """
        if self.status == "playing" and not self.revealed[r][c]:
            self.flags[r][c] = not self.flags[r][c]

    def _check_win(self) -> bool:
        """
        すべての安全なタイルが開かれたかチェックします。
        """
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] != -1 and not self.revealed[r][c]:
                    return False
        return True


def init_minesweeper_state(w: int = 8, h: int = 8, mines: int = 10) -> MinesweeperState:
    """
    初期状態の MinesweeperState を生成します。
    """
    state = MinesweeperState(width=w, height=h, num_mines=mines)
    state.reset()
    return state
