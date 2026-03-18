import json
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
    cell_list: list[Minesweeper3DCell] = Field(default_factory=list)
    game_over: bool = False
    won: bool = False

    @property
    def total_cells(self) -> int:
        return self.width * self.height * self.depth

    def get_cell(self, x: int, y: int, z: int) -> Minesweeper3DCell | None:
        if not (0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.depth):
            return None
        idx = x + (y * self.width) + (z * self.width * self.height)
        if 0 <= idx < len(self.cell_list):
            return self.cell_list[idx]
        return None

    def to_compact_data(self) -> dict[str, Any]:
        """
        JS側に渡すデータを極限まで軽量化した辞書形式。
        """
        # セルデータを [状態, 周囲の地雷数] のペアのフラットリストに変換
        # 状態: 0=未開封, 1=開封済, 2=フラグ, 3=地雷(開封)
        flat_cells = []
        for c in self.cell_list:
            status = 0
            if c.opened:
                status = 3 if c.is_mine else 1
            elif c.flagged:
                status = 2
            flat_cells.extend([status, c.neighbor_mines])

        return {
            "w": self.width,
            "h": self.height,
            "d": self.depth,
            "m": self.total_mines,
            "go": self.game_over,
            "wn": self.won,
            "c": flat_cells,
        }

    def generate_safe_html(self, css: str, js: str) -> str:
        """
        TypeError を完全に排除するための最終安定版 HTML 生成。
        """
        # コンパクトなデータを JSON 化
        data_json = json.dumps(self.to_compact_data())

        # テンプレート
        # f-string を避け、単純な連結で構築。波括弧のパースエラーを完全に防ぐ。
        html_parts = [
            '<!DOCTYPE html><html><head><meta charset="utf-8"><style>',
            css.replace("\n", ""),
            '</style></head><body style="margin:0;padding:0;overflow:hidden;background:#111;">',
            '<div id="m3d-container" style="width:100vw;height:100vh;"></div>',
            '<script id="m3d-data" type="application/json">',
            data_json,
            "</script>",
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>',
            '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>',
            "<script>",
            'window.Streamlit={setComponentValue:function(v){window.parent.postMessage({type:"streamlit:setComponentValue",value:v},"*");}};',
            js,
            'try{const d=JSON.parse(document.getElementById("m3d-data").textContent);if(window.initMinesweeper3D)window.initMinesweeper3D(d);}catch(e){console.error(e);}',
            "</script></body></html>",
        ]
        return "".join(html_parts)


def create_minesweeper_3d(width: int, height: int, depth: int, mines: int) -> Minesweeper3DState:
    state = Minesweeper3DState(width=width, height=height, depth=depth, total_mines=mines)
    cells = []
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                cells.append(Minesweeper3DCell(x=x, y=y, z=z))
    state.cell_list = cells
    all_indices = list(range(len(state.cell_list)))
    mine_indices = random.sample(all_indices, min(mines, len(all_indices)))
    for idx in mine_indices:
        state.cell_list[idx].is_mine = True
    for cell in state.cell_list:
        if cell.is_mine:
            continue
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    neighbor = state.get_cell(cell.x + dx, cell.y + dy, cell.z + dz)
                    if neighbor and neighbor.is_mine:
                        count += 1
        cell.neighbor_mines = count
    return state


def open_cell_3d(state: Minesweeper3DState, x: int, y: int, z: int) -> Minesweeper3DState:
    if state.game_over or state.won:
        return state
    cell = state.get_cell(x, y, z)
    if not cell or cell.opened or cell.flagged:
        return state
    cell.opened = True
    if cell.is_mine:
        state.game_over = True
        for c in state.cell_list:
            if c.is_mine:
                c.opened = True
        return state
    safe_unopened = [c for c in state.cell_list if not c.is_mine and not c.opened]
    if not safe_unopened:
        state.won = True
        return state
    if cell.neighbor_mines == 0:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    open_cell_3d(state, x + dx, y + dy, z + dz)
    return state


def toggle_flag_3d(state: Minesweeper3DState, x: int, y: int, z: int) -> Minesweeper3DState:
    cell = state.get_cell(x, y, z)
    if cell and not cell.opened:
        cell.flagged = not cell.flagged
    return state


def migrate_minesweeper_3d_data(data: Any) -> Minesweeper3DState | None:
    if not data:
        return None
    try:
        if isinstance(data, dict):
            if "cells" in data and "cell_list" not in data:
                data["cell_list"] = list(data["cells"].values())
            return Minesweeper3DState(**data)
        return None
    except Exception:
        return None
