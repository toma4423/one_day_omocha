from src.utils.concentration import Card, ConcentrationGameState, create_deck, handle_card_click


def test_create_deck():
    deck = create_deck(num_pairs=13, use_all_suits=False)
    assert len(deck) == 26
    assert sum(1 for c in deck if c.rank == "A") == 2


def test_handle_card_click_match():
    # 同一ランクのカードを2枚用意
    cards = [
        Card(id=0, rank="A", suit="♠"),
        Card(id=1, rank="A", suit="♥"),
        Card(id=2, rank="2", suit="♠"),
    ]
    state = ConcentrationGameState(cards=cards, mode="single")

    # 1枚目
    state = handle_card_click(state, 0)
    assert state.cards[0].is_flipped is True
    assert len(state.selected_indices) == 1

    # 2枚目 (マッチ)
    state = handle_card_click(state, 1)
    assert state.cards[0].is_matched is True
    assert state.cards[1].is_matched is True
    assert state.scores[0] == 1


def test_handle_card_click_mismatch():
    cards = [
        Card(id=0, rank="A", suit="♠"),
        Card(id=1, rank="2", suit="♥"),
    ]
    state = ConcentrationGameState(cards=cards, mode="single")

    state = handle_card_click(state, 0)
    state = handle_card_click(state, 1)

    assert state.cards[0].is_matched is False
    assert state.cards[1].is_matched is False
    # 3枚目（リストを拡張してから新しい状態を作成）
    state.cards.append(Card(id=2, rank="3", suit="♠"))
    state = handle_card_click(state, 2)
    assert state.cards[0].is_flipped is False
    assert state.cards[1].is_flipped is False
