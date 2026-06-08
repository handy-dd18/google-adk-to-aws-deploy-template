# アーキテクチャ詳細

## 全体構成図

```
ユーザー
  │
  ▼
API Gateway (HTTP API / POST /query)
  │
  ▼
AWS Lambda (Python 3.12)
  ├── AWS Strands Agents Runtime
  │   ├── Orchestrator Agent   ← Amazon Bedrock (Claude)
  │   ├── Data Retrieval Agent ← Amazon Bedrock (Claude) + Athena Tool
  │   ├── Preprocessing Agent  ← Amazon Bedrock (Claude) + Preprocess Tool
  │   └── Response Agent       ← Amazon Bedrock (Claude)
  │
  ├── Amazon Athena (Workgroup: cost-limited)
  │   └── Amazon Glue Data Catalog
  │       └── S3 Tables (Iceberg)
  │
  └── Amazon S3
      ├── s3-data-bucket/           # Iceberg テーブル
      └── s3-athena-results-bucket/ # クエリ結果 (30日TTL)
```

## エージェント間のデータフロー

1. ユーザーが自然言語クエリを POST /query で送信
2. Lambda が AWS Strands Agent を起動
3. **Orchestrator Agent** がクエリを解釈し、Data Retrieval Agent に転送
4. **Data Retrieval Agent** が SQL を生成 → `run_athena_query` ツールで Athena 実行 → 結果 JSON
5. **Preprocessing Agent** が結果 JSON を受け取り → `preprocess_data` ツールで前処理 → 処理済み JSON
6. **Response Agent** が処理結果を自然言語でまとめてユーザーに返却

## 選定理由

| コンポーネント | 選定理由 |
|---|---|
| Lambda + API Gateway | EC2不要・従量課金・オートスケール |
| S3 Tables (Iceberg) | 低コストなオープンテーブルフォーマット・スキーマ進化に対応 |
| Athena | サーバーレスSQL・S3への直接クエリ・スキャン量課金 |
| Amazon Bedrock | API呼び出し型・モデル管理不要・IAM統合 |
| AWS Strands Agents | AWSネイティブなマルチエージェントフレームワーク |

## スケーリング考慮事項

- Lambdaの同時実行数制限 (デフォルト1000) に注意
- Athenaの同時クエリ上限 (デフォルト20) に注意
- 長時間クエリ (>15分) が必要な場合は Step Functions + Athena を検討
