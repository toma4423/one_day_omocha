
def test_sync_data_structure():
    """同期用データの構造が正しいか検証"""
    sync_data = {"x": 100, "y": -50, "scale": 1.2, "mode": "weekly"}
    assert isinstance(sync_data["x"], int)
    assert isinstance(sync_data["y"], int)
    assert isinstance(sync_data["scale"], float)
    assert sync_data["mode"] in ["weekly", "monthly"]

def test_session_state_update_simulation():
    """session_stateへの反映シミュレーション"""
    # 模擬的なsession_state
    session_state = {"w_x": 0, "w_y": 0, "w_scale": 1.0}
    sync_data = {"x": 150, "y": 200, "scale": 1.5}
    
    # 反映処理
    session_state["w_x"] = sync_data["x"]
    session_state["w_y"] = sync_data["y"]
    session_state["w_scale"] = sync_data["scale"]
    
    assert session_state["w_x"] == 150
    assert session_state["w_y"] == 200
    assert session_state["w_scale"] == 1.5
