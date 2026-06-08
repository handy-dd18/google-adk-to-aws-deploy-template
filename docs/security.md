# セキュリティガイドライン

## IAM 最小権限

- Lambda 実行ロールは AWS SAM テンプレート (`infra/sam/template.yaml`) で最小権限を定義
- Bedrock: `bedrock:InvokeModel` のみ、特定モデル ARN に限定
- Athena: 指定 Workgroup・データベースのみ
- S3: 読み取り専用 (データバケット)、書き込みは結果バケットのみ
- DDL/DML は Lambda から実行不可（Athena Workgroup 設定 + SELECT のみポリシーで二重防御）

## データ保護

- S3 バケット: SSE-KMS 暗号化 + パブリックアクセスブロック
- Athena 結果: SSE-KMS 暗号化 + 30日自動削除
- Bedrock 呼び出し: TLS 通信のみ（AWS SDK デフォルト）
- Secrets: AWS Secrets Manager で管理（ソースコードに認証情報を書かない）

## ネットワーク

- Lambda は VPC 外 (パブリック)で動作可（VPC 外の方がコストと管理コストが低い）
- 機密データを扱う場合は VPC 内 Lambda + VPC Endpoint (Bedrock / S3 / Athena) を検討

## 監査・ログ

- CloudTrail: Athena/Bedrock/S3 への API コールを記録
- CloudWatch Logs: Lambda / API Gateway のアクセスログ (30日保持)
- S3 アクセスログ: データバケットへのアクセスを別バケットに記録

## Athena クエリ制御

- Workgroup の `bytes_scanned_cutoff_per_query` でスキャン上限を設定（デフォルト 1 GB）
- `enforce_workgroup_configuration = true` でクライアント側の設定上書きを禁止

## 本番前チェックリスト

- [ ] API Gateway に Cognito Authorizer または Lambda Authorizer を設定
- [ ] CORS の `allow_origins` を本番ドメインに制限
- [ ] KMS キーのキーポリシーを最小権限に
- [ ] AWS Budgets で Bedrock / Athena / Lambda の予算アラートを設定
- [ ] CloudTrail のログを S3 に長期保存（コンプライアンス要件に応じて）
