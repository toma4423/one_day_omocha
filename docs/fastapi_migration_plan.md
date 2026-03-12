# FastAPI 移行計画書 (FastAPI Migration Plan)

## 1. 目的
現在の Streamlit ベースのモノリス構成から、FastAPI + React (Next.js) + Rust (WASM) のモダンなアーキテクチャへ移行し、以下の目標を達成する。
- **圧倒的な高速化**: 重い計算（画像処理等）を Rust/WASM でエッジ（ブラウザ）へ分散。
- **高いスケーラビリティ**: GCP のサーバーレス技術を活用し、ユーザー増に対応。
- **保守性の向上**: フロントエンドとバックエンドを疎結合にし、API-First な開発を徹底。

## 2. ターゲット・アーキテクチャ
- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: Next.js (TypeScript) + Tailwind CSS
- **Core Logic**: Rust (PyO3 for Backend / WASM for Frontend)
- **Infrastructure**: Google Cloud Platform (GCP)

## 3. インフラ構成 (GCP)
使用する主要なサービスとその役割を以下に定義する。

| サービス | 役割 | 理由 |
| :--- | :--- | :--- |
| **Cloud Run** | API サーバー & フロントエンド | サーバーレスでオートスケール、リクエストがない時はコストゼロ。 |
| **Artifact Registry** | Docker イメージ管理 | Cloud Run デプロイ用のコンテナイメージを格納。 |
| **Cloud Build** | CI/CD パイプライン | GitHub へのプッシュを検知して自動ビルド・デプロイ。 |
| **Cloud Storage** | 画像等の一時保存 | 高速かつ安価なオブジェクトストレージ。 |
| **Cloud Logging** | ログ管理 | エラー監視と分析。 |

## 4. 事前準備 (GCP)
移行作業を開始する前に、以下の準備を行う必要がある。

1.  **GCP プロジェクトの作成**: 新規プロジェクト（例: `one-day-omocha-prod`）を作成。
2.  **API の有効化**:
    - Cloud Run API
    - Artifact Registry API
    - Cloud Build API
3.  **gcloud CLI のインストール**: ローカル環境から操作できるよう設定。
    - `gcloud auth login`
    - `gcloud config set project [PROJECT_ID]`
4.  **サービスアカウントの設定**: Cloud Build 等に必要な権限（roles/run.admin 等）を付与。

## 5. 移行ロードマップ

### Phase 1: 共通コアの確立 (完了済み・継続中)
- `src/utils/` の Pydantic モデル化（FastAPI の Schema として転用可能にする）。
- ロジックと UI (Streamlit) の完全分離。

### Phase 2: モノレポ構成への移行
- `uv` ワークスペースを導入し、ディレクトリを以下のように再編。
    - `/core`: 共通ロジック (Python / Rust)
    - `/backend`: FastAPI プロジェクト
    - `/frontend`: Next.js プロジェクト
    - `/streamlit_legacy`: 現在の Streamlit 版（並行稼働用）

### Phase 3: FastAPI エンドポイントの実装
- 各おもちゃのロジックを API エンドポイントとして公開。
- OpenAPI (Swagger) ドキュメントの自動生成。

### Phase 4: フロントエンド開発 & WASM 導入
- Next.js での UI 実装。
- 画像処理等の重いロジックを Rust で WASM 化し、ブラウザ側で実行。

### Phase 5: GCP デプロイ & CI/CD
- `Dockerfile` の作成。
- GitHub Actions または Cloud Build による自動デプロイ環境の構築。

## 6. 具体的なデプロイ手順 (Cloud Run)

1.  **Artifact Registry リポジトリ作成**:
    ```bash
    gcloud artifacts repositories create repo-name --repository-format=docker --location=asia-northeast1
    ```
2.  **イメージのビルドとプッシュ**:
    ```bash
    gcloud builds submit --tag asia-northeast1-docker.pkg.dev/[PROJECT_ID]/repo-name/api-image .
    ```
3.  **Cloud Run へデプロイ**:
    ```bash
    gcloud run deploy api-service --image asia-northeast1-docker.pkg.dev/[PROJECT_ID]/repo-name/api-image --platform managed --region asia-northeast1 --allow-unauthenticated
    ```

## 7. 注意事項
- **認証**: パブリックに公開するおもちゃ箱のため、基本は `allow-unauthenticated` とするが、将来的なユーザー管理導入時は Cloud Identity Platform を検討する。
- **コスト**: Cloud Run は「無料枠」が大きいため、個人開発規模であればほぼ無料で運用可能。
