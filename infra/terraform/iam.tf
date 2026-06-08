# ─────────────────────────────────────────────
# Lambda 実行ロール
# ─────────────────────────────────────────────
resource "aws_iam_role" "lambda_exec" {
  name = "${local.name_prefix}-lambda-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ─────────────────────────────────────────────
# Lambda 用カスタムポリシー（最小権限）
# ─────────────────────────────────────────────
resource "aws_iam_policy" "lambda_app" {
  name        = "${local.name_prefix}-lambda-app-policy"
  description = "Strands Agent App Lambda に必要な最小権限"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Athena クエリ実行
      {
        Sid    = "AthenaQuery"
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution",
          "athena:ListQueryExecutions"
        ]
        Resource = aws_athena_workgroup.default.arn
      },
      # S3 データバケット読み取り
      {
        Sid    = "S3DataRead"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:ListBucket"]
        Resource = [
          aws_s3_bucket.data.arn,
          "${aws_s3_bucket.data.arn}/*"
        ]
      },
      # Athena クエリ結果バケットへの読み書き
      {
        Sid    = "S3AthenaResults"
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"]
        Resource = [
          aws_s3_bucket.athena_results.arn,
          "${aws_s3_bucket.athena_results.arn}/*"
        ]
      },
      # Amazon Bedrock モデル呼び出し
      {
        Sid    = "BedrockInvoke"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"
      },
      # Glue Data Catalog（Athena が利用）- 特定データベース/テーブルに限定
      {
        Sid    = "GlueCatalog"
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:GetPartitions"
        ]
        Resource = [
          "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:catalog",
          "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:database/${aws_glue_catalog_database.main.name}",
          "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${aws_glue_catalog_database.main.name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_app" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_app.arn
}
