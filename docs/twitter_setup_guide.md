# Twitter (X) 連携機能 実装準備ガイド

このドキュメントは、パルム週間予定表から Twitter (X) へ直接画像をポストする機能を実装するための、事前設定および調査事項をまとめたものです。

---

## 1. Twitter (X) 側での事前設定

実装には [X Developer Portal](https://developer.x.com/) でのアプリ登録が必要です。

### 1.1 開発者アカウントの作成
- **プラン**: 「Free（無料）」プランで問題ありません。
- **制限**: 月間 1,500 ポストまで無料。画像アップロードの可否については、以下の設定を確認してください。

### 1.2 アプリの設定 (Project & App)
1.  **App Permissions (重要)**:
    - デフォルトは `Read Only` です。必ず **`Read and Write`** に変更してください。
    - これを忘れると「画像投稿（Write操作）」でエラーが発生します。
2.  **Type of App**:
    - `Web App, Automated App or Bot` を選択してください。
3.  **App info**:
    - `Callback URL` 等は、現状では `http://localhost` などのダミー設定で構いません（将来的に「Twitterでログイン」を実装する場合は本番URLが必要になります）。

### 1.3 取得が必要な情報 (Credentials)
設定完了後、`Keys and Tokens` タブから以下の **4つのキー** を取得し、安全な場所にメモしてください。
- **API Key** (Consumer Key)
- **API Key Secret** (Consumer Secret)
- **Access Token**
- **Access Token Secret**
  - ※ Access Token の権限が `Created with Read and Write permissions` になっていることを確認してください。

---

## 2. 技術的な調査・検討事項

実装開始前に、プログラム側で以下の点を検証します。

### 2.1 APIバージョンの使い分け
- **テキスト投稿**: API v2 を使用します。
- **画像アップロード**: Twitter API の仕様上、メディア（画像）のアップロードには API v1.1 のエンドポイントを併用する必要があります。
- **ライブラリ**: Python の `tweepy` を使用し、v1.1 と v2 をシームレスに扱えるか確認します。

### 2.2 画像のハンドリング
- **一時保存**: Streamlit Cloud などの環境制限を考慮し、生成した画像をファイルとして保存せず、`io.BytesIO` (メモリ) を介して直接アップロードするフローを検討します。
- **ファイルサイズ**: Twitter の制限（通常 5MB 以下）に収まるよう、画像生成時の最適化を確認します。

### 2.3 セキュリティ
- **認証情報の保存**: `Access Token` 等をブラウザの LocalStorage に保存する際、平文での保存を避ける仕組み、または「投稿時のみ入力する」ユーザー体験（UX）の検討が必要です。

---

## 3. 今後の実装ステップ案

1.  **環境構築**: `pyproject.toml` に `tweepy` を追加。
2.  **ロジック実装**: `src/utils/twitter.py` (新規) に投稿関数を定義。
3.  **UI実装**: パルム予定表のページに「Twitter設定」および「今すぐポスト」ボタンを追加。
4.  **検証**: 実際に画像付きポストが成功することを確認。

---
作成日: 2026-03-03
対象機能: パルム週間予定表 Twitter 連携
