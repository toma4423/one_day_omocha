import random

from pydantic import BaseModel, Field


class Card(BaseModel):
    """トランプのカードを定義するモデル"""

    rank: str  # "A", "2", ..., "K"
    suit: str  # "♠", "♥", "♣", "♦"
    id: int = 0
    is_flipped: bool = False
    is_matched: bool = False

    @property
    def display_value(self) -> str:
        return f"{self.suit}{self.rank}"

    @property
    def is_red(self) -> bool:
        return self.suit in ["♥", "♦"]


class ConcentrationGameState(BaseModel):
    """神経衰弱のゲーム状態を管理するモデル"""

    cards: list[Card] = Field(default_factory=list)
    mode: str = "battle"  # "single" or "battle"
    current_player: int = 0  # 0 or 1
    scores: list[int] = Field(default_factory=lambda: [0, 0])
    selected_indices: list[int] = Field(default_factory=list)
    message: str = "プレイヤー1の番です"
    game_over: bool = False
    use_all_suits: bool = False
    move_count: int = 0  # 1人プレイ用の手数


def create_deck(num_pairs: int = 13, use_all_suits: bool = False) -> list[Card]:
    """
    指定された条件でデッキを作成します。
    """
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["♠", "♥", "♣", "♦"] if use_all_suits else ["♠", "♥"]

    selected_ranks = ranks[:num_pairs]
    deck = []
    card_id = 0

    for rank in selected_ranks:
        for suit in suits:
            deck.append(Card(id=card_id, rank=rank, suit=suit))
            card_id += 1

    random.shuffle(deck)
    return deck


def handle_card_click(state: ConcentrationGameState, index: int) -> ConcentrationGameState:
    """
    カードがクリックされた時の状態遷移ロジック。
    """
    if state.game_over or state.cards[index].is_matched:
        return state

    # 既に2枚めくられている状態で新しいのをめくろうとしたら、前のを伏せる
    if len(state.selected_indices) >= 2:
        for idx in state.selected_indices:
            state.cards[idx].is_flipped = False
        state.selected_indices = []

    if index in state.selected_indices:
        return state

    state.cards[index].is_flipped = True
    state.selected_indices.append(index)

    if len(state.selected_indices) == 2:
        state.move_count += 1
        idx1, idx2 = state.selected_indices
        card1, card2 = state.cards[idx1], state.cards[idx2]

        if card1.rank == card2.rank:
            # マッチ成功
            card1.is_matched = True
            card2.is_matched = True
            state.scores[state.current_player] += 1

            if state.mode == "battle":
                state.message = f"プレイヤー{state.current_player + 1}がマッチ成功！もう一度引けます。"
            else:
                state.message = "マッチ成功！"

            # 全カードマッチ判定
            if all(c.is_matched for c in state.cards):
                state.game_over = True
                if state.mode == "battle":
                    if state.scores[0] > state.scores[1]:
                        state.message = f"ゲーム終了！ プレイヤー1の勝利！ ({state.scores[0]}対{state.scores[1]})"
                    elif state.scores[1] > state.scores[0]:
                        state.message = f"ゲーム終了！ プレイヤー2の勝利！ ({state.scores[1]}対{state.scores[0]})"
                    else:
                        state.message = "ゲーム終了！ 引き分けです。"
                else:
                    state.message = f"クリアおめでとうございます！ (手数: {state.move_count})"
        else:
            # マッチ失敗
            if state.mode == "battle":
                state.current_player = 1 - state.current_player
                state.message = f"残念！ 次はプレイヤー{state.current_player + 1}の番です。"
            else:
                state.message = "残念！ 次はどのカードをめくりますか？"

    return state
