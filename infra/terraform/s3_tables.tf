# ─────────────────────────────────────────────
# S3 Tables 用データバケット（Iceberg テーブル格納）
# ─────────────────────────────────────────────
resource "aws_s3_bucket" "data" {
  bucket = "${local.name_prefix}-data"
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ─────────────────────────────────────────────
# S3 Tables バケット設定（Table Bucket API）
# ※ aws_s3tables_table_bucket は aws provider v5.50+ で利用可能
# ─────────────────────────────────────────────
resource "aws_s3tables_table_bucket" "main" {
  name = "${local.name_prefix}-table-bucket"
}

resource "aws_s3tables_namespace" "main" {
  table_bucket_arn = aws_s3tables_table_bucket.main.arn
  namespace        = ["${var.project_name}_${var.environment}"]
}

# サンプルテーブル（実際のスキーマに合わせて変更してください）
resource "aws_s3tables_table" "sample" {
  table_bucket_arn = aws_s3tables_table_bucket.main.arn
  namespace        = aws_s3tables_namespace.main.namespace[0]
  name             = "sample_table"
  format           = "ICEBERG"
}

# ─────────────────────────────────────────────
# Athena クエリ結果用バケット
# ─────────────────────────────────────────────
resource "aws_s3_bucket" "athena_results" {
  bucket = "${local.name_prefix}-athena-results"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "athena_results" {
  bucket                  = aws_s3_bucket.athena_results.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 30日でクエリ結果を自動削除（コスト最適化）
resource "aws_s3_bucket_lifecycle_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id
  rule {
    id     = "expire-query-results"
    status = "Enabled"
    expiration { days = 30 }
  }
}
