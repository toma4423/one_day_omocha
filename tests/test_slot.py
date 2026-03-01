from src.utils.slot import (
    calculate_probabilities,
    evaluate_slot_spin,
    migrate_slot_config,
    resolve_pattern_to_chars,
    solve_weights_from_targets,
    spin_reels,
    validate_slot_config,
)


def test_validate_slot_config_success():
    valid_config = {
        "name": "Test",
        "symbols": [{"id": 1, "char": "A"}],
        "payouts": [{"name": "W", "pattern": [1, 1, 1]}],
    }
    is_valid, msg = validate_slot_config(valid_config)
    assert is_valid is True


def test_validate_slot_config_fail_duplicate():
    invalid_config = {
        "name": "Test",
        "symbols": [{"id": 1, "char": "A"}, {"id": 1, "char": "B"}],
        "payouts": [{"name": "W", "pattern": [1, 1, 1]}],
    }
    is_valid, msg = validate_slot_config(invalid_config)
    assert is_valid is False
    assert "IDが重複" in msg


def test_validate_slot_config_fail_invalid_id():
    invalid_config = {
        "name": "Test",
        "symbols": [{"id": 1, "char": "A"}],
        "payouts": [{"name": "W", "pattern": [1, 99, 1]}],
    }
    is_valid, msg = validate_slot_config(invalid_config)
    assert is_valid is False
    assert "存在しない図柄ID" in msg


def test_migrate_slot_config_legacy():
    # 1. 非常に古い形式（文字列リストのシンボル、文字ベースのパターン）
    legacy_config = {
        "name": "旧スロット",
        "symbols": ["🍎", "🍇"],
        "payouts": [
            {"name": "りんご3つ", "pattern": ["🍎", "🍎", "🍎"], "score": 100},
        ],
    }

    migrated = migrate_slot_config(legacy_config)

    # シンボルが辞書形式になり、IDが付与されていること
    assert migrated["symbols"][0]["char"] == "🍎"
    assert migrated["symbols"][0]["id"] == 1
    assert migrated["symbols"][1]["char"] == "🍇"
    assert migrated["symbols"][1]["id"] == 2

    # 役のパターンがID（数字）に変換されていること
    assert migrated["payouts"][0]["pattern"] == [1, 1, 1]


def test_migrate_slot_config_incomplete_dict():
    # 2. 不完全な辞書形式（IDやimage_urlが欠落、文字ベースのパターン）
    incomplete_config = {
        "symbols": [
            {"char": "7️⃣", "weight": 5.0},
            {"char": "⭐"},
        ],
        "payouts": [
            {"name": "セブン", "pattern": ["7️⃣", "7️⃣", "7️⃣"], "score": 777},
        ],
    }

    migrated = migrate_slot_config(incomplete_config)

    # IDとデフォルト値が補完されていること
    assert migrated["symbols"][0]["id"] == 1
    assert migrated["symbols"][0]["weight"] == 5.0
    assert migrated["symbols"][0]["image_url"] is None
    assert migrated["symbols"][1]["id"] == 2
    assert migrated["symbols"][1]["weight"] == 1.0

    # パターンがIDに紐付いていること
    assert migrated["payouts"][0]["pattern"] == [1, 1, 1]


def test_migration_and_evaluation_linkage():
    # 3. 実際の利用シーン：外部データを読み込んで判定まで正しく行えるか
    external_data = {
        "symbols": [{"char": "X"}, {"char": "Y"}],
        "payouts": [{"name": "WinX", "pattern": ["X", "X", "X"], "score": 10}],
    }

    # マイグレーション実行
    config = migrate_slot_config(external_data)

    # スピン結果（マイグレーション後のシンボルを使用）
    # ID=1 (X) が3つ揃った状態をシミュレート
    spin_result = [config["symbols"][0], config["symbols"][0], config["symbols"][0]]

    # 判定
    result = evaluate_slot_spin(spin_result, config["payouts"])

    assert result is not None
    assert result["name"] == "WinX"
    assert result["score"] == 10


def test_resolve_pattern_to_chars():
    symbols = [
        {"id": 1, "char": "🍒"},
        {"id": 2, "char": "🍋"},
    ]
    pattern = [1, 1, "ANY"]
    resolved = resolve_pattern_to_chars(pattern, symbols)
    assert resolved == ["🍒", "🍒", "ANY"]

    # 未定義IDのフォールバック
    assert resolve_pattern_to_chars([99], symbols) == ["99"]


def test_spin_reels():
    symbol_data = [
        {"id": 1, "char": "A", "weight": 1, "image_url": None},
        {"id": 2, "char": "B", "weight": 1, "image_url": "http://example.com/b.png"},
        {"id": 3, "char": "C", "weight": 1, "image_url": None},
    ]
    result = spin_reels(symbol_data, 3)
    assert len(result) == 3
    # 戻り値が辞書のリストであることを確認
    for item in result:
        assert isinstance(item, dict)
        assert "id" in item
        assert "char" in item
        assert "image_url" in item


def test_spin_reels_weighted():
    # 重みが極端な場合
    symbol_data = [
        {"id": 1, "char": "A", "weight": 1000, "image_url": None},
        {"id": 2, "char": "B", "weight": 0, "image_url": None},
    ]
    result = spin_reels(symbol_data, 10)
    for item in result:
        assert item["char"] == "A"


def test_evaluate_slot_spin_exact_match():
    payouts = [
        {"pattern": [1, 1, 1], "name": "JACKPOT", "score": 1000},
        {"pattern": [2, 2, 2], "name": "AAA", "score": 100},
    ]

    # 成立 (辞書のリストを渡す)
    res = evaluate_slot_spin(
        [
            {"id": 1, "char": "7", "image_url": None},
            {"id": 1, "char": "7", "image_url": None},
            {"id": 1, "char": "7", "image_url": None},
        ],
        payouts,
    )
    assert res is not None
    assert res["name"] == "JACKPOT"

    # 不成立
    res = evaluate_slot_spin(
        [
            {"id": 1, "char": "7", "image_url": None},
            {"id": 1, "char": "7", "image_url": None},
            {"id": 2, "char": "A", "image_url": None},
        ],
        payouts,
    )
    assert res is None


def test_evaluate_slot_spin_any_match():
    payouts = [
        {"pattern": [1, 1, "ANY"], "name": "CHERRY_2", "score": 10},
    ]

    # 成立
    res = evaluate_slot_spin(
        [
            {"id": 1, "char": "🍒", "image_url": None},
            {"id": 1, "char": "🍒", "image_url": None},
            {"id": 3, "char": "🍇", "image_url": None},
        ],
        payouts,
    )
    assert res is not None
    assert res["name"] == "CHERRY_2"


def test_calculate_probabilities_basic():
    # シンプルな設定: 2種類の図柄が等確率
    symbols = [
        {"id": 1, "char": "A", "weight": 1.0},
        {"id": 2, "char": "B", "weight": 1.0},
    ]
    payouts = [
        {"name": "AAA", "pattern": [1, 1, 1]},
        {"name": "A-ANY", "pattern": [1, "ANY", "ANY"]},
    ]

    probs = calculate_probabilities(symbols, payouts)

    # AAA の確率は (1/2)^3 = 1/8 = 12.5%
    # A-ANY の確率は (1/2) * 1 * 1 = 50%
    # ただし、calculate_probabilities 内で最初にマッチした役が優先されるロジック
    hit_rates = {r["name"]: r["rate"] for r in probs["hit_rates"]}
    assert hit_rates["AAA"] == 12.5
    # AAAが先に判定されるため、A-ANY は 50% - 12.5% = 37.5% になる
    assert hit_rates["A-ANY"] == 37.5


def test_solve_weights_from_targets_basic():
    symbols = [
        {"id": 1, "char": "7", "weight": 1.0},
        {"id": 2, "char": "Blank", "weight": 1.0},
    ]
    payouts = [
        {"name": "JACKPOT", "pattern": [1, 1, 1]},
    ]
    targets = {"JACKPOT": 10.0}  # 10%で当たるようにしたい

    new_symbols = solve_weights_from_targets(symbols, payouts, targets)

    # 10% の JACKPOT (1,1,1) ならば、p(1)^3 = 0.1 => p(1) = 0.1^(1/3) ≒ 0.464
    s1 = next(s for s in new_symbols if s["id"] == 1)
    s2 = next(s for s in new_symbols if s["id"] == 2)

    total_w = s1["weight"] + s2["weight"]
    prob1 = s1["weight"] / total_w
    # prob1^3 が 10% に近いことを確認
    assert 0.09 <= (prob1**3) <= 0.11
