# 2026-03-17 Pandas から Polars への移行

## 概要
プロジェクトのモダン化とパフォーマンス向上、および依存関係の最適化のため、データ処理ライブラリを Pandas から **Polars** へ完全に移行しました。

## 変更内容
### 1. 依存関係の更新
- `pyproject.toml` および `requirements.txt` から `pandas` を削除。
- `polars` を追加（Rust ベースの高速なデータ処理ライブラリ）。

### 2. コードの移行 (4ページ)
以下のページにおいて、Pandas 特有の書き方を Polars 互換に書き換えました。
- 🎲 サイコロ
- 🎲 チンチロ
- 🎰 スロット
- ⚙️ スロット作成

主な変更点：
- `import pandas as pd` → `import polars as pl`
- `pd.DataFrame` → `pl.DataFrame`
- 列名の変更を `rename()` や `with_columns()` を用いた Polars 形式へ。
- CSV出力を `write_csv()` へ。
- 要素への関数適用を `map_elements()` (Polars) へ。

### 3. メリット
- **高速化**: 大量のデータ処理において Rust の恩恵を受けられます。
- **軽量化**: デプロイ時のライブラリサイズが Pandas (numpy依存) に比べて最適化されます。
- **APIの一貫性**: Pydantic モデルとの親和性が高く、メソッドチェーンを用いた直感的な記述が可能になりました。

## 品質管理
- **自動テスト**: 全 95 項目のテストがパス。
- **静的解析**: Ruff および Mypy を全てクリア。
