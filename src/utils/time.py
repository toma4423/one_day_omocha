from datetime import datetime, timedelta, timezone

def get_jst_now() -> datetime:
    """
    日本標準時 (JST, UTC+9) の現在時刻を返します。
    """
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst)
