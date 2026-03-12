from pydantic import BaseModel


class CounterItem(BaseModel):
    """個別のカウンターを定義するモデル"""

    label: str
    count: int = 0
    weight: float = 1.0


class CountSupportSession(BaseModel):
    """カウントサポートのセッション全体を定義するモデル"""

    items: list[CounterItem] = []


def calculate_weighted_value(value: float, weight: float) -> float:
    """
    数値に重みを掛けた値を計算します。
    """
    return round(value * weight, 1)


def calculate_diff_xy(x_val: float, y_val: float) -> float:
    """
    XとYの差分を計算します。
    """
    return round(x_val - y_val, 1)


def calculate_final_score(x_val: float, y_val: float, z_val: float) -> float:
    """
    (X - Y) - Z の最終スコアを計算します。
    """
    return round(x_val - y_val - z_val, 1)
