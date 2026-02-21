import pytest
from datetime import datetime, timedelta, timezone
from src.utils.time import get_jst_now

def test_get_jst_now_is_japan_time():
    # 実行時の時刻を取得
    now = get_jst_now()
    
    # タイムゾーンが UTC+9 であることを確認
    assert now.tzinfo is not None
    assert now.tzinfo.utcoffset(now) == timedelta(hours=9)
    
    # タイムゾーンを除去した UTC 時刻を取得し、9時間を足して比較する
    # get_jst_now は内部で datetime.now(jst) を呼んでいるため
    # その時点のシステム時刻（UTC）+ 9h とほぼ一致するはず
    utc_now = datetime.now(timezone.utc)
    
    # どちらも absolute time として比較
    # (JST時刻) と (UTC時刻) の時間差は 0 であるべき
    diff = now - utc_now
    assert abs(diff.total_seconds()) < 1.0 # 1秒以内の誤差
