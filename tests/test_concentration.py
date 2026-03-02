from src.utils.concentration import Card, GameState, create_deck, handle_card_click


def test_create_deck_easy():
    # 初級モード (2スート)
    deck = create_deck(13, use_all_suits=False)
    assert len(deck) == 26
    # ♠か♥のみであることを確認
    for c in deck:
        assert c.suit in ["♠", "♥"]

def test_create_deck_hard():
    # 上級モード (4スート)
    deck = create_deck(13, use_all_suits=True)
    assert len(deck) == 52
    # 全スート含まれているか確認
    suits = set(c.suit for c in deck)
    assert suits == {"♠", "♥", "♣", "♦"}

def test_card_color_property():
    red_card = Card(id=0, rank="A", suit="♥")
    black_card = Card(id=1, rank="A", suit="♠")
    assert red_card.is_red == True
    assert black_card.is_red == False

def test_handle_card_click_sequence():
    deck = create_deck(13)
    state = GameState(cards=deck)
    # 1枚目
    state = handle_card_click(state, 0)
    assert state.cards[0].is_flipped == True
    # 2枚目 (ミスマッチを想定してランクを変える)
    state.cards[0].rank = "A"
    state.cards[1].rank = "K"
    state = handle_card_click(state, 1)
    assert len(state.selected_indices) == 2
    # 3枚目をクリックした瞬間に前の2枚が伏せられる
    state = handle_card_click(state, 2)
    assert state.cards[0].is_flipped == False
    assert state.cards[1].is_flipped == False
    assert state.cards[2].is_flipped == True
    assert len(state.selected_indices) == 1
