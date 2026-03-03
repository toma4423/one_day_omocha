from src.utils.concentration import Card, GameState, create_deck, handle_card_click


def test_create_deck():
    # デフォルト (13ペア = 26枚)
    deck = create_deck(13, use_all_suits=False)
    assert len(deck) == 26
    
    # 全スート (13ペア * 4スート = 52枚)
    deck_full = create_deck(13, use_all_suits=True)
    assert len(deck_full) == 52


def test_handle_card_click_match():
    # 同じ数字のカードを2枚用意
    cards = [
        Card(id=0, rank="A", suit="♠"),
        Card(id=1, rank="A", suit="♥"),
    ]
    state = GameState(cards=cards, mode="battle")
    
    # 1枚目めくる
    state = handle_card_click(state, 0)
    assert state.cards[0].is_flipped is True
    assert len(state.selected_indices) == 1
    
    # 2枚目めくる -> マッチ
    state = handle_card_click(state, 1)
    assert state.cards[0].is_matched is True
    assert state.cards[1].is_matched is True
    assert state.scores[0] == 1
    assert state.current_player == 0  # マッチしたので交代しない


def test_handle_card_click_mismatch():
    # 違う数字のカードを用意
    cards = [
        Card(id=0, rank="A", suit="♠"),
        Card(id=1, rank="2", suit="♥"),
    ]
    state = GameState(cards=cards, mode="battle")
    
    # 1枚目
    state = handle_card_click(state, 0)
    # 2枚目 -> ミス
    state = handle_card_click(state, 1)
    
    assert state.cards[0].is_matched is False
    assert state.scores[0] == 0
    assert state.current_player == 1  # ミスしたので交代


def test_handle_card_click_single_mode():
    # 1人プレイモードのテスト
    cards = [
        Card(id=0, rank="A", suit="♠"),
        Card(id=1, rank="2", suit="♥"),
    ]
    state = GameState(cards=cards, mode="single")
    
    # 1枚目
    state = handle_card_click(state, 0)
    # 2枚目 -> ミス
    state = handle_card_click(state, 1)
    
    assert state.current_player == 0  # 1人プレイなので交代しない
    assert state.move_count == 1      # 2枚めくった時点で1手とカウント


def test_game_over():
    cards = [
        Card(id=0, rank="A", suit="♠"),
        Card(id=1, rank="A", suit="♥"),
    ]
    state = GameState(cards=cards, mode="battle")
    
    handle_card_click(state, 0)
    handle_card_click(state, 1)
    
    assert state.game_over is True
