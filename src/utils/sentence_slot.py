import random
from typing import Any

from pydantic import BaseModel, Field


class SentenceSlotReel(BaseModel):
    """単一のリールの設定と項目を保持するモデル"""

    name: str
    items: list[str] = Field(default_factory=list)


class SentenceSlotConfig(BaseModel):
    """文章スロット全体の設定を保持するモデル"""

    reels: list[SentenceSlotReel] = Field(
        default_factory=lambda: [
            SentenceSlotReel(name="誰が", items=["お父さんが", "宇宙人が", "猫が", "名探偵が", "勇者が"]),
            SentenceSlotReel(name="何を", items=["カレーを", "秘密を", "バナナを", "スマホを", "伝説の剣を"]),
            SentenceSlotReel(name="どうした", items=["食べた", "投げた", "壊した", "隠した", "磨いた"]),
        ]
    )


def pick_random_item(items: list[str]) -> str:
    """リストから均等な確率で一つ項目を選択します。"""
    if not items:
        return ""
    return random.choice(items)


def migrate_sentence_slot_data(data: Any) -> SentenceSlotConfig:
    """外部データから SentenceSlotConfig を安全に復元します。"""
    if not data:
        return SentenceSlotConfig()

    try:
        if isinstance(data, dict) and "reels" in data:
            return SentenceSlotConfig(**data)
        return SentenceSlotConfig()
    except Exception:
        return SentenceSlotConfig()
