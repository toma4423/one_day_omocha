# 2026-03-04 黒ひげ危機一発 & マインスイーパーの大規模リファクタリング

## 変更内容
- **黒ひげ危機一発**:
    - `src/utils/kurohige.py`: `KurohigeState` (Pydantic) モデルを導入。ロジックをカプセル化。
    - `src/assets/kurohige/`: JS/CSS コンポーネントを作成。タルとアニメーションの演出を実装。
    - `pages/12_☠️_黒ひげ危機一発.py`: 新しいロジックとJSコンポーネントを統合。`SafeStorage` による永続化を強化。
- **マインスイーパー**:
    - `src/utils/minesweeper.py`: `MinesweeperState` (Pydantic) モデルを導入。`numpy` 依存を排除し、シリアライズ可能な構造に刷新。
    - `src/assets/minesweeper/`: JS/CSS によるグリッド表示を実装。右クリックによるフラグ操作をサポート。
    - `pages/13_💣_マインスイーパー.py`: 新しいロジックとJSコンポーネントを統合。

## 理由
- Streamlit のボタンによるグリッド描画は再描画が重く、UXを損なっていた。
- マインスイーパーで右クリックが使えない制約を、JSコンポーネントの導入により解消。
- プロジェクトの最新ルール（Pydantic, ロジック分離, API-First）に準拠させるため。

## 検証
- `uv run pytest tests/test_kurohige.py tests/test_minesweeper.py` をパス。
- `ruff` / `mypy` による品質チェックをパス。
