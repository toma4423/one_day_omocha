# 2026-03-13 画像エディタの実装

## 概要
複数のデバイス（Android/iPhone）で撮影された画像の向きを正しく補正し、指定されたアスペクト比（9:16など）で切り抜き、ズーム、リサイズができる「画像エディタ」を追加しました。

## 変更内容
- `src/utils/image_editor.py`: Pydantic を使用した画像処理パラメータ管理と、Pillow による画像加工ロジック。
    - `load_image_with_orientation`: EXIF情報の `Orientation` に基づく自動回転補正。
    - `process_image`: アスペクト比切り抜き、スケーリング、リサイズ、フォーマット変換。
- `pages/26_🖼️_画像エディタ.py`: Streamlit による UI。
    - プリセット（1:1, 16:9, 9:16, 4:3, 3:4）およびカスタム比率の選択。
    - ズーム、位置調整（オフセット）、出力幅、出力形式の調整。
    - `SafeStorage` によるリロード時の画像データ復元。
- `tests/test_image_editor.py`: コアロジックの単体テスト。

## 技術的ポイント
- **EXIF補正**: モバイルデバイス特有の画像向き問題を `ImageOps.exif_transpose` で解決。
- **UIとロジックの分離**: `GEMINI.md` に従い、Streamlit に依存しない純粋な Python 関数として画像処理を実装。
- **Pydantic**: パラメータのバリデーションと構造化。
- **リロード対策**: `SafeStorage` を使用し、画像データを base64 形式でブラウザの LocalStorage に保存。
