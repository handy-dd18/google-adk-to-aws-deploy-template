variable "aws_region" {
  description = "AWSリージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "プロジェクト名（リソース名のプレフィックスに使用）"
  type        = string
  default     = "strands-aws-template"
}

variable "environment" {
  description = "デプロイ環境（dev / stg / prod）"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "environment は dev / stg / prod のいずれかを指定してください。"
  }
}

variable "bedrock_model_id" {
  description = "使用する Bedrock モデル ID"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}

variable "lambda_timeout_seconds" {
  description = "Lambda タイムアウト（秒）"
  type        = number
  default     = 120
}

variable "lambda_memory_mb" {
  description = "Lambda メモリ（MB）"
  type        = number
  default     = 512
}

variable "athena_workgroup_bytes_scanned_limit" {
  description = "Athena Workgroup 1クエリあたりのスキャン上限（バイト）。デフォルト1GB"
  type        = number
  default     = 1073741824
}

variable "cors_allow_origins" {
  description = "API Gateway CORS で許可するオリジンのリスト。本番では特定ドメインに制限してください。"
  type        = list(string)
  default     = ["*"]
}
