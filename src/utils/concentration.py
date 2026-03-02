import random
from dataclasses import dataclass, field


@dataclass
class Card:
    id: int
    rank: str  # "A", "2", ..., "K"
    suit: str  # "♠", "♥", "♣", "♦"
    is_flipped: bool = False
    is_matched: bool = False

    @property
    def display_value(self) -> str:
        return f"{self.suit}{self.rank}"


@dataclass
class GameState:
    cards: list[Card]
    current_player: int = 0  # 0 or 1
    scores: list[int] = field(default_factory=lambda: [0, 0])
    selected_indices: list[int] = field(default_factory=list)
    message: str = "プレイヤー1の番です"
    game_over: bool = False


def create_deck(num_pairs: int = 13) -> list[Card]:
    """
    指定されたペア数のデッキを作成します。
    デフォルトは13ペア（26枚）。
    """
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["♠", "♥", "♣", "♦"]
    
    selected_ranks = ranks[:num_pairs]
    deck = []
    card_id = 0
    
    # 2つのスートを使用してペアを作る
    for rank in selected_ranks:
        for suit in suits[:2]:
            deck.append(Card(id=card_id, rank=rank, suit=suit))
            card_id += 1
            
    random.shuffle(deck)
    return deck


def handle_card_click(state: GameState, index: int) -> GameState:
    """
    カードがクリックされた時の状態遷移ロジック。
    """
    # ゲーム終了、またはすでにマッチ済みのカードは無視
    if state.game_over or state.cards[index].is_matched:
        return state

    # すでに2枚めくられている場合は、まずそれらを戻す（次のターンの開始）
    if len(state.selected_indices) >= 2:
        for idx in state.selected_indices:
            state.cards[idx].is_flipped = False
        state.selected_indices = []

    # めくられている最中のカードを再度クリックした場合は無視
    if index in state.selected_indices:
        return state

    # 新しくカードをめくる
    state.cards[index].is_flipped = True
    state.selected_indices.append(index)

    # 2枚めくった時の判定
    if len(state.selected_indices) == 2:
        idx1, idx2 = state.selected_indices
        card1, card2 = state.cards[idx1], state.cards[idx2]

        if card1.rank == card2.rank:
            # マッチ成功
            card1.is_matched = True
            card2.is_matched = True
            state.scores[state.current_player] += 1
            state.message = f"プレイヤー{state.current_player + 1}がマッチ成功！もう一度引けます。"
            # 全てマッチしたか確認
            if all(c.is_matched for c in state.cards):
                state.game_over = True
                if state.scores[0] > state.scores[1]:
                    state.message = "ゲーム終了！ プレイヤー1の勝利！"
                elif state.scores[1] > state.scores[0]:
                    state.message = "ゲーム終了！ プレイヤー2の勝利！"
                else:
                    state.message = "ゲーム終了！ 引き分けです。"
        else:
            # マッチ失敗（手番交代）
            state.message = f"残念！ 次はプレイヤー{(1 - state.current_player) + 1}の番です。"
            state.current_player = 1 - state.current_player

    return state
