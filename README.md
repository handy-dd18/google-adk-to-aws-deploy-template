# google-adk-to-aws-deploy-template
AWS Strands Agentsを利用してAWS上にAIアプリケーションを構築するテンプレート

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
- **IaC**: Terraform

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

## 開発計画（手動実装 + AI補助前提）
- [ ] フェーズ1: Terraformで最小インフラ（S3 Tables/Athena/IAM/Logging）を定義
- [ ] フェーズ2: AWS Strands Agentsのマルチエージェント骨組みを実装
- [ ] フェーズ3: Athenaクエリ実行ツールとPython前処理ツールを実装
- [ ] フェーズ4: Lambda + API Gatewayへのデプロイを実装
- [ ] フェーズ5: セキュリティ設定とコスト監視を強化

## 推奨フォルダ構成
```text
.
├── infra/
│   └── terraform/
│       ├── providers.tf
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       ├── iam.tf
│       ├── athena.tf
│       ├── s3_tables.tf
│       └── lambda_api.tf
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
