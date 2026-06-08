# コスト最適化ガイドライン

## コスト要因と対策

| サービス | コスト要因 | 対策 |
|---|---|---|
| Amazon Bedrock | トークン数 | プロンプトを簡潔に / キャッシュ活用 |
| Amazon Athena | スキャンデータ量 | Workgroup のスキャン上限 / WHERE 句必須 / Iceberg パーティション活用 |
| AWS Lambda | 実行時間・メモリ | タイムアウト・メモリを用途別に最適化 |
| Amazon S3 | ストレージ・リクエスト数 | ライフサイクルポリシーで不要データ削除 / S3 Intelligent-Tiering |
| API Gateway | リクエスト数 | HTTP API (REST API より安価) を選択 |

## Terraform 変数でのチューニング

```hcl
# 小規模開発環境の設定例
lambda_timeout_seconds               = 60
lambda_memory_mb                     = 256
athena_workgroup_bytes_scanned_limit = 536870912  # 512 MB
```

## 予算アラート設定（推奨）

AWS Budgets で以下のアラートを設定してください（Terraform 未管理のため手動設定）：

- **全体月次予算**: 上限の 80% で SNS 通知
- **Bedrock 月次予算**: $X で通知
- **Athena 月次予算**: $X で通知

## Athena コスト削減のベストプラクティス

1. S3 Tables (Iceberg) のパーティションを日付・カテゴリで設定
2. クエリ結果をキャッシュ（同一クエリの再実行を避ける）
3. SELECT \* ではなく必要カラムのみ取得
4. Athena Workgroup の `bytes_scanned_cutoff_per_query` を設定済み

## Lambda コスト削減のベストプラクティス

1. コールドスタートを減らす（Provisioned Concurrency は常時稼働になるため非推奨）
2. メモリを増やすと CPU 比例向上 → 実行時間短縮で総コストが下がる場合がある
3. Bedrock のストリーミングレスポンスを活用してタイムアウトを回避

## 月次コスト概算（小規模PoC: 100リクエスト/日）

| サービス | 概算 |
|---|---|
| Lambda | < $1 |
| API Gateway | < $1 |
| Athena | $1〜5 (クエリ量依存) |
| Bedrock (Claude Sonnet) | $5〜20 (トークン量依存) |
| S3 | < $1 |
| **合計** | **$7〜27/月** |

> 上記はあくまで概算です。実際の利用量で変動します。
