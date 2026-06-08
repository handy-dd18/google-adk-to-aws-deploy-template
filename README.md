# google-adk-to-aws-deploy-template
AWS Strands Agentsを利用してAWS上にAIアプリケーションを構築するテンプレート（SAM + Terraform 分離）

## 目的
AWS Strands Agentsで構築したマルチエージェントAIアプリを、AWSのマネージドサービス中心（常時稼働サーバーなし）で動かすための設計・実装ガイドです。

## 想定アーキテクチャ（初期案）
- **アプリ実行基盤**: AWS Lambda + API Gateway（HTTP API）
- **認証**: Amazon Cognito（必要に応じて）
- **AIモデル**: Amazon Bedrock
- **データ基盤**: Amazon S3 Tables（Iceberg）
- **クエリエンジン**: Amazon Athena
- **監査/ログ**: CloudWatch Logs, CloudTrail
- **秘密情報管理**: AWS Secrets Manager
- **IaC**: AWS SAM（アプリ実行基盤）+ Terraform（データ基盤）

> EC2などの常時稼働サーバーを避け、従量課金のサーバーレス構成を基本とします。

## マルチエージェント設計（AWS Strands Agents）
1. **Orchestrator Agent**
   - ユーザー自然言語を解釈し、各エージェントへタスク分配
2. **Data Retrieval Agent**
   - AthenaへSQLを発行し、S3 Tables上データを取得
3. **Preprocessing Agent**
   - 取得データをPythonで前処理（欠損値処理、型変換、簡易集計）
4. **Response Agent**
   - 処理結果をユーザー向けに要約・整形して返却

## セキュリティとコスト最適化の基本方針
- 最小権限IAM（Lambda実行ロールを用途別に分離）
- S3暗号化（SSE-KMS）とAthena出力先バケット制御
- Bedrock/Athena/Logsの利用量監視と予算アラート（AWS Budgets）
- Lambdaのメモリ/タイムアウトを用途別に最適化
- クエリ制限（Athena Workgroup設定）で過剰スキャンを抑制

## デプロイ方針（SAM中心）
- **AWS SAM**: Lambda / API Gateway(HTTP API) / 実行ロールをデプロイ
- **Terraform**: S3 Tables / S3 / Athena / Glue などデータ基盤をデプロイ
- Terraform出力値（Workgroup名、Database名、Bucket名）を SAM パラメータに渡して連携

## ローカル実行方針（Floci前提）
- `APP_EXECUTION_MODE=local` でローカルモードを有効化
- `FLOCI_ATHENA_ENDPOINT_URL` を設定すると Athena クライアント接続先を Floci に切替
- `LOCAL_ATHENA_STUB_ROWS` を設定すると Athena 呼び出しを行わずスタブ結果を返却
- `LOCAL_MODE_SQL` を設定するとローカルモード時に SQL 実行疎通を確認可能

## ローカル実行手順（SAM local + Floci）
1. Floci を起動
   - `cd infra/floci && docker compose up -d`
2. SAM ローカル用環境変数ファイルを作成
   - `cp infra/sam/local-env.example.json infra/sam/local-env.json`
3. Lambda/API をローカル起動
   - `cd infra/sam && sam build --template-file template.yaml`
   - `sam local start-api --env-vars local-env.json --template-file template.yaml`
4. 動作確認
   - `curl -X POST http://127.0.0.1:3000/query -H "Content-Type: application/json" -d '{"query":"売上を要約して"}'`

## AWSデプロイ手順（SAM + Terraform）
1. データ基盤を Terraform で作成
   - `cd infra/terraform && terraform init && terraform apply`
2. Terraform 出力値を確認
   - `terraform output athena_workgroup_name`
   - `terraform output glue_database_name`
   - `terraform output athena_results_bucket_name`
   - `terraform output s3_data_bucket_name`
3. `infra/sam/samconfig.toml` の `parameter_overrides` を更新
4. SAM で Lambda/API Gateway をデプロイ
   - `cd infra/sam && sam build --template-file template.yaml`
   - `sam deploy --config-env default`

## 推奨フォルダ構成
```text
.
├── infra/
│   ├── terraform/
│   │   ├── providers.tf
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── athena.tf
│   │   └── s3_tables.tf
│   ├── sam/
│   │   ├── template.yaml
│   │   ├── samconfig.toml
│   │   └── local-env.example.json
│   └── floci/
│       └── docker-compose.yml
├── app/
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── data_retrieval_agent.py
│   │   ├── preprocessing_agent.py
│   │   └── response_agent.py
│   ├── tools/
│   │   ├── athena_query_tool.py
│   │   └── python_preprocess_tool.py
│   ├── prompts/
│   └── main.py
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    ├── architecture.md
    ├── security.md
    └── cost-optimization.md
```

## ホスティング未確定時の推奨方針
現時点では **Lambda + API Gateway** を第一候補とし、将来的に要件（長時間処理/双方向通信）が増えた場合のみ
AWS Fargate等を再評価します。

## テスト
- Unit テスト: `python -m pytest tests/unit/ -v`
