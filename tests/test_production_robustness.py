import polars as pl

from src.utils.image_maker import FONT_DIR, get_available_fonts, get_font


def test_polars_compatibility_dice():
    """サイコロ履歴の Polars 変換が正しく行えるか検証"""
    history = [{"時刻": "12:00:00", "設定": "1d6", "出目合計": 6}]
    df = pl.DataFrame(history)
    assert isinstance(df, pl.DataFrame)
    assert df.shape == (1, 3)
    assert df["出目合計"][0] == 6


def test_font_absolute_fallback():
    """フォントが完全に欠落している状況でも文字化けを回避できるか検証"""
    # 存在しないフォント名
    font = get_font("NOT_EXIST_FONT_12345", 24)
    assert font is not None
    # 少なくともデフォルトフォントか標準フォントが返っていること
    assert hasattr(font, "getmask")


def test_corrupted_font_protection():
    """ファイルが破損（極小サイズ）している場合に標準フォントへ切り替わるか検証"""
    dummy_file = FONT_DIR / "corrupted_test.ttf"
    try:
        # 10バイトの偽ファイルを生成
        dummy_file.write_bytes(b"too small")
        # get_available_fonts がこれを無視することを確認
        fonts = get_available_fonts()
        assert "corrupted_test" not in fonts

        # 直接読み込もうとしても get_font が安全に処理することを確認
        font = get_font("corrupted_test", 20)
        assert font is not None
    finally:
        if dummy_file.exists():
            dummy_file.unlink()


def test_polars_empty_dataframe():
    """空のデータでも Polars がエラーを吐かずに DataFrame を作れるか検証"""
    empty_list = []
    # Pandas と違い、Polars は空リストからの推論に型が必要な場合があるが、
    # 辞書リストであれば問題ないはず
    df = pl.DataFrame(empty_list)
    assert df.is_empty()
