# 🎯 新規おもちゃ（ページ）作成作業依頼書

## 1. 概要 (Feature Overview)
- **おもちゃの名前**: [例：リバーシ]
- **機能概要**: [例：8x8の盤面で石を交互に置き、挟んで裏返すゲーム。対人戦。]
- **保存データ**: [例：現在の盤面状態、手番、勝利数（LocalStorage 保存対象）]

## 2. 開発要件 (Development Requirements)
本プロジェクトの **`GEMINI.md`** および **`README.md`** の規約に厳格に従って実装してください。

### アーキテクチャ原則
1. **ロジックの完全分離**: 
   - 状態管理、ルール判定、計算処理などはすべて `src/utils/[おもちゃ名].py` に Python 純粋関数として実装する。
   - `src/utils/` 内（`styles.py` を除く）では `streamlit` をインポートしない。
2. **状態管理の統一**:
   - LocalStorage へのアクセスは必ず `src/utils/storage.py` の `SafeStorage` を介して行う。
3. **UI の共通化**:
   - 盤面がある場合は `src/utils/styles.py` の `render_grid_board` を使用する。
   - サイドバー最下部に `render_donation_box` を配置する。

## 3. 推奨実装フロー (Implementation Flow)
以下の順序で作業を行い、各ステップで進捗を報告してください。

1. **研究 (Research)**:
   - 既存の `src/utils/storage.py` や `src/utils/styles.py` を確認し、再利用可能な要素を特定する。
2. **戦略 (Strategy)**:
   - 必要な関数（ロジック）と UI 構成案を作成し、ユーザーに提示する。
3. **実行 (Execution)**:
   - **Step A: ロジック実装**: `src/utils/[おもちゃ名].py` を作成。
   - **Step B: テスト作成**: `tests/test_[おもちゃ名].py` を作成し、`uv run pytest` で合格を確認。
   - **Step C: UI 実装**: `pages/X_🎨_[おもちゃ名].py` を作成。`SafeStorage` を使用して状態を復元・保存する。
4. **検証 (Validation)**:
   - `uv run ruff check . --fix`
   - `uv run ruff format .`
   - `uv run mypy src`
   - すべてのテストがパスし、型エラーがないことを確認。

## 4. 指示事項 (Instructions for AI)
あなたはシニアソフトウェアエンジニアとして、上記要件に基づき **自律的** に実装を行ってください。
- 実装前に `GEMINI.md` を読み、プロジェクト固有のルールを理解すること。
- テストコードは、境界値や異常系を含め網羅的に記述すること。
- 完成後は、作業内容を `history/` フォルダに記録すること。
