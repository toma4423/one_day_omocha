import json

from src.utils.minesweeper_3d import create_minesweeper_3d


def test_compact_data_structure():
    """超軽量データ（フラット配列）の構造を検証"""
    state = create_minesweeper_3d(2, 2, 2, 2)
    data = state.to_compact_data()

    assert data["w"] == 2
    assert data["h"] == 2
    assert data["d"] == 2
    assert isinstance(data["c"], list)
    # 8セル * 2要素([status, neighbors]) = 16要素
    assert len(data["c"]) == 16
    # 状態の値が 0-3 の範囲にあること
    assert all(0 <= s <= 3 for s in data["c"][::2])


def test_html_type_safety_strict():
    """TypeErrorを防ぐための最終的な型チェック"""
    state = create_minesweeper_3d(3, 3, 3, 5)
    html = state.generate_safe_html("css", "js")

    # Python 3.13 / Streamlit Cloud で必須の文字列型であることを保証
    assert type(html) is str
    assert len(html) > 0
    # 特殊文字によるエスケープ崩れがないか
    assert "<script" in html
    assert "</script>" in html


def test_data_size_minimization():
    """データサイズが劇的に削減されていることを検証"""
    # 10x10x10 = 1000マス
    state = create_minesweeper_3d(10, 10, 10, 100)
    data_json = json.dumps(state.to_compact_data())

    # 以前の方式（約95KB）から大幅に削減されていることを期待
    # 1000マス * 2要素([0,0]) + 構造体 = 約 5KB - 10KB 程度になるはず
    assert len(data_json) < 15000
    print(f"Compact JSON size: {len(data_json)} bytes")


def test_initialization_with_empty_state():
    """初期化時のエッジケース"""
    state = create_minesweeper_3d(1, 1, 1, 0)
    assert state.total_cells == 1
    assert len(state.cell_list) == 1
