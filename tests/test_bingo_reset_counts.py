
def test_bingo_label_preservation_on_count_reset():
    """
    カウントリセット時にラベルが保持されるロジックのシミュレーションテスト
    """
    # 1. 初期状態
    session_state = {
        "csb_rows": 2,
        "csb_cols": 2,
        "csb_label_0_0": "保持したい名前",
        "csb_count_0_0": 5,
        "csb_reset_id": 0
    }
    
    # 2. カウントリセット実行（実際のページのロジックを模擬）
    def run_count_reset(state):
        # カウントだけを0にする
        for r in range(state["csb_rows"]):
            for c in range(state["csb_cols"]):
                key = f"csb_count_{r}_{c}"
                if key in state:
                    state[key] = 0
        # reset_idをインクリメント
        state["csb_reset_id"] += 1
        return state

    # 実行
    result_state = run_count_reset(session_state)
    
    # 3. 検証
    assert result_state["csb_count_0_0"] == 0
    assert result_state["csb_label_0_0"] == "保持したい名前" # ラベルが消えていないこと
    assert result_state["csb_reset_id"] == 1
