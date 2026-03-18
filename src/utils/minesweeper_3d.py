import random
from typing import Any

from pydantic import BaseModel, Field


class Minesweeper3DCell(BaseModel):
    """3次元空間の1つのセルの状態を保持するモデル"""

    x: int
    y: int
    z: int
    is_mine: bool = False
    opened: bool = False
    flagged: bool = False
    neighbor_mines: int = 0


class Minesweeper3DState(BaseModel):
    """3Dマインスイーパーのゲーム全体の状態を管理するモデル"""

    width: int
    height: int
    depth: int
    total_mines: int
    cells: dict[str, Minesweeper3DCell] = Field(default_factory=dict)
    game_over: bool = False
    won: bool = False

    @property
    def total_cells(self) -> int:
        return self.width * self.height * self.depth

    def get_cell_key(self, x: int, y: int, z: int) -> str:
        return f"{x},{y},{z}"

    def get_cell(self, x: int, y: int, z: int) -> Minesweeper3DCell | None:
        return self.cells.get(self.get_cell_key(x, y, z))


def create_minesweeper_3d(width: int, height: int, depth: int, mines: int) -> Minesweeper3DState:
    """3Dマインスイーパーの初期状態を生成します。"""
    state = Minesweeper3DState(width=width, height=height, depth=depth, total_mines=mines)

    # 全セルの生成
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                key = state.get_cell_key(x, y, z)
                state.cells[key] = Minesweeper3DCell(x=x, y=y, z=z)

    # 地雷の配置
    all_keys = list(state.cells.keys())
    mine_keys = random.sample(all_keys, min(mines, len(all_keys)))
    for key in mine_keys:
        state.cells[key].is_mine = True

    # 周囲の地雷数を計算 (26近傍)
    for x in range(width):
        for y in range(height):
            for z in range(depth):
                cell = state.get_cell(x, y, z)
                if not cell or cell.is_mine:
                    continue

                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        for dz in [-1, 0, 1]:
                            if dx == 0 and dy == 0 and dz == 0:
                                continue
                            neighbor = state.get_cell(x + dx, y + dy, z + dz)
                            if neighbor and neighbor.is_mine:
                                count += 1
                cell.neighbor_mines = count

    return state


def open_cell_3d(state: Minesweeper3DState, x: int, y: int, z: int) -> Minesweeper3DState:
    """特定のセルを開きます。0の場合は周囲26マスを再帰的に開きます。"""
    if state.game_over or state.won:
        return state

    cell = state.get_cell(x, y, z)
    if not cell or cell.opened or cell.flagged:
        return state

    cell.opened = True

    # 地雷を踏んだ場合
    if cell.is_mine:
        state.game_over = True
        # 全ての地雷を表示
        for c in state.cells.values():
            if c.is_mine:
                c.opened = True
        return state

    # 勝利判定
    unopened_safe_cells = [c for c in state.cells.values() if not c.is_mine and not c.opened]
    if not unopened_safe_cells:
        state.won = True
        return state

    # 0の場合は周囲を自動オープン (Flood Fill)
    if cell.neighbor_mines == 0:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    open_cell_3d(state, x + dx, y + dy, z + dz)

    return state


def toggle_flag_3d(state: Minesweeper3DState, x: int, y: int, z: int) -> Minesweeper3DState:
    """フラグの立て降ろしを行います。"""
    if state.game_over or state.won:
        return state

    cell = state.get_cell(x, y, z)
    if cell and not cell.opened:
        cell.flagged = not cell.flagged

    return state


def migrate_minesweeper_3d_data(data: Any) -> Minesweeper3DState | None:
    """保存されたデータから復元します。"""
    if not data:
        return None
    try:
        # data["cells"] があることを確認
        if isinstance(data, dict) and "cells" in data:
            return Minesweeper3DState(**data)
        return None
    except Exception:
        return None
