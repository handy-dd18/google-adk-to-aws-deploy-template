# ─────────────────────────────────────────────
# Lambda 関数（Strands Agent アプリ本体）
# ─────────────────────────────────────────────
data "archive_file" "app" {
  type        = "zip"
  source_dir  = "${path.module}/../../app"
  output_path = "${path.module}/../../.build/app.zip"
}

resource "aws_lambda_function" "app" {
  function_name    = "${local.name_prefix}-app"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "main.handler"
  runtime          = "python3.12"
  timeout          = var.lambda_timeout_seconds
  memory_size      = var.lambda_memory_mb

  filename         = data.archive_file.app.output_path
  source_code_hash = data.archive_file.app.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT      = var.environment
      BEDROCK_MODEL_ID = var.bedrock_model_id
      ATHENA_WORKGROUP = aws_athena_workgroup.default.name
      ATHENA_DATABASE  = aws_glue_catalog_database.main.name
      ATHENA_RESULTS_BUCKET = aws_s3_bucket.athena_results.bucket
    }
  }
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/lambda/${aws_lambda_function.app.function_name}"
  retention_in_days = 30
}

# ─────────────────────────────────────────────
# API Gateway (HTTP API)
# ─────────────────────────────────────────────
resource "aws_apigatewayv2_api" "app" {
  name          = "${local.name_prefix}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = var.cors_allow_origins
    allow_methods = ["POST"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }
}

resource "aws_apigatewayv2_integration" "app" {
  api_id                 = aws_apigatewayv2_api.app.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.app.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "query" {
  api_id    = aws_apigatewayv2_api.app.id
  route_key = "POST /query"
  target    = "integrations/${aws_apigatewayv2_integration.app.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.app.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api.arn
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/apigateway/${aws_apigatewayv2_api.app.name}"
  retention_in_days = 30
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.app.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.app.execution_arn}/*/*"
}
