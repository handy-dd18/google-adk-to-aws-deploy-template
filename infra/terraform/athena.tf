# ─────────────────────────────────────────────
# Athena Workgroup
# ─────────────────────────────────────────────
resource "aws_athena_workgroup" "default" {
  name  = "${local.name_prefix}-workgroup"
  state = "ENABLED"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/results/"
      encryption_configuration {
        encryption_option = "SSE_KMS"
      }
    }

    # コスト抑制：1クエリあたりのスキャン上限
    bytes_scanned_cutoff_per_query = var.athena_workgroup_bytes_scanned_limit

    engine_version {
      selected_engine_version = "Athena engine version 3"
    }
  }
}

# ─────────────────────────────────────────────
# Glue Data Catalog（Athena から S3 Tables を参照）
# ─────────────────────────────────────────────
resource "aws_glue_catalog_database" "main" {
  name        = replace("${local.name_prefix}_db", "-", "_")
  description = "Strands Agent テンプレート用 Glue データベース（S3 Tables / Iceberg）"
}
