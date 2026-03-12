from pydantic import BaseModel, Field


class CounterItem(BaseModel):
    """個別のカウンターを定義するモデル"""

    label: str
    count: int = 0
    weight: float = 1.0


class CountSupportSession(BaseModel):
    """カウントサポートのセッション全体を定義するモデル"""

    items: list[CounterItem] = []


class BingoCell(BaseModel):
    """ビンゴの個別のセルを定義するモデル"""

    label: str
    count: int = 0


class BingoBoard(BaseModel):
    """ビンゴの盤面全体を定義するモデル"""

    rows: int = Field(default=5, ge=1, le=15)
    cols: int = Field(default=5, ge=1, le=15)
    cells: dict[str, BingoCell] = {}  # key: "r_c"

    def get_cell(self, r: int, c: int) -> BingoCell:
        """指定された座標のセルを取得します。存在しない場合は初期化します。"""
        key = f"{r}_{c}"
        if key not in self.cells:
            self.cells[key] = BingoCell(label=f"項目 {r + 1}-{c + 1}")
        return self.cells[key]

    def reset_counts_only(self) -> None:
        """項目名はそのままに、カウントのみを0にリセットします。"""
        # 既存の全セルを0にする
        for cell in self.cells.values():
            cell.count = 0
        # まだ生成されていないセルのために、デフォルト値を意識する必要があるが、
        # 基本的には cells 辞書にあるものだけでOK（get_cellで0がデフォルトなので）

    def reset_all(self) -> None:
        """項目名とカウントを全て初期化します。"""
        self.cells = {}


def calculate_weighted_value(value: float, weight: float) -> float:
    """数値に重みを掛けた値を計算します。"""
    return round(value * weight, 1)


def calculate_diff_xy(x_val: float, y_val: float) -> float:
    """XとYの差分を計算します。"""
    return round(x_val - y_val, 1)


def calculate_final_score(x_val: float, y_val: float, z_val: float) -> float:
    """(X - Y) - Z の最終スコアを計算します。"""
    return round(x_val - y_val - z_val, 1)
