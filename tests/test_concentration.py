from src.utils.concentration import Card, GameState, create_deck, handle_card_click


def test_create_deck():
    deck = create_deck(13)
    assert len(deck) == 26
    # ペアになっているか確認
    ranks = [c.rank for c in deck]
    for r in ["A", "2", "J", "Q", "K"]:
        assert ranks.count(r) == 2

def test_handle_card_click_first_card():
    deck = create_deck(13)
    state = GameState(cards=deck)
    state = handle_card_click(state, 0)
    assert state.cards[0].is_flipped == True
    assert len(state.selected_indices) == 1

def test_handle_card_click_match_success():
    # 強制的に同じランクのカードを配置
    card1 = Card(id=0, rank="A", suit="♠")
    card2 = Card(id=1, rank="A", suit="♥")
    state = GameState(cards=[card1, card2])
    
    state = handle_card_click(state, 0)
    state = handle_card_click(state, 1)
    
    assert state.cards[0].is_matched == True
    assert state.cards[1].is_matched == True
    assert state.scores[0] == 1
    assert state.current_player == 0 # 継続
    assert state.game_over == True

def test_handle_card_click_match_fail():
    # 違うランクのカードを配置
    card1 = Card(id=0, rank="A", suit="♠")
    card2 = Card(id=1, rank="K", suit="♥")
    state = GameState(cards=[card1, card2], current_player=0)
    
    state = handle_card_click(state, 0)
    state = handle_card_click(state, 1)
    
    assert state.cards[0].is_matched == False
    assert state.current_player == 1 # 交代
    assert len(state.selected_indices) == 2 # まだめくられた状態
    
    # 次のクリックで裏返ることを確認
    state = handle_card_click(state, 0) # 実際にはありえない操作だがロジック検証
    # selected_indicesがリセットされているはず
    assert len(state.selected_indices) == 1
