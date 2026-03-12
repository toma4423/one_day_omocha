from src.utils.count_support import BingoBoard


def test_bingo_reset_counts_only():
    board = BingoBoard(rows=3, cols=3)
    # セルを設定
    cell = board.get_cell(0, 0)
    cell.label = "テスト項目"
    cell.count = 5

    board.reset_counts_only()

    # 項目名は維持され、カウントのみ0になる
    assert board.get_cell(0, 0).label == "テスト項目"
    assert board.get_cell(0, 0).count == 0


def test_bingo_reset_all():
    board = BingoBoard(rows=3, cols=3)
    cell = board.get_cell(0, 0)
    cell.label = "テスト項目"
    cell.count = 5

    board.reset_all()

    # 全て初期化される
    # get_cell するとデフォルト値で再生成される
    new_cell = board.get_cell(0, 0)
    assert new_cell.label == "項目 1-1"
    assert new_cell.count == 0


def test_bingo_serialization():
    # JSON出力・入力のテスト
    board = BingoBoard(rows=2, cols=2)
    board.get_cell(0, 0).label = "保存テスト"
    board.get_cell(0, 0).count = 10

    dump = board.model_dump()
    new_board = BingoBoard(**dump)

    assert new_board.rows == 2
    assert new_board.get_cell(0, 0).label == "保存テスト"
    assert new_board.get_cell(0, 0).count == 10
