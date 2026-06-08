output "api_gateway_endpoint" {
  description = "API Gateway のエンドポイント URL"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "lambda_function_name" {
  description = "Lambda 関数名"
  value       = aws_lambda_function.app.function_name
}

output "s3_data_bucket_name" {
  description = "S3 Tables データバケット名"
  value       = aws_s3_bucket.data.bucket
}

output "athena_workgroup_name" {
  description = "Athena Workgroup 名"
  value       = aws_athena_workgroup.default.name
}
