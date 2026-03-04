import random
from typing import Literal

from pydantic import BaseModel, Field


class KurohigeState(BaseModel):
    """
    黒ひげ危機一発のゲーム状態を管理するモデルです。
    """

    num_slots: int = Field(12, ge=4, le=24)
    target_slot: int = -1
    clicked_slots: list[int] = Field(default_factory=list)
    status: Literal["ready", "playing", "boom"] = "ready"

    def reset(self, num_slots: int | None = None) -> None:
        """
        ゲームをリセットします。
        """
        if num_slots is not None:
            self.num_slots = num_slots
        self.target_slot = random.randint(0, self.num_slots - 1)
        self.clicked_slots = []
        self.status = "playing"

    def click_slot(self, idx: int) -> str:
        """
        スロットをクリック（剣を刺す）します。
        """
        if self.status != "playing" or idx in self.clicked_slots:
            return self.status

        if idx == self.target_slot:
            self.status = "boom"
        else:
            self.clicked_slots.append(idx)

        return self.status


def init_kurohige_state(num_slots: int = 12) -> KurohigeState:
    """
    初期状態の KurohigeState を生成します。
    """
    state = KurohigeState(num_slots=num_slots)
    state.reset()
    return state
