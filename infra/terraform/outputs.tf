output "s3_data_bucket_name" {
  description = "S3 Tables データバケット名"
  value       = aws_s3_bucket.data.bucket
}

output "athena_results_bucket_name" {
  description = "Athena クエリ結果バケット名"
  value       = aws_s3_bucket.athena_results.bucket
}

output "athena_workgroup_name" {
  description = "Athena Workgroup 名"
  value       = aws_athena_workgroup.default.name
}

output "glue_database_name" {
  description = "Glue Catalog Database 名"
  value       = aws_glue_catalog_database.main.name
}
