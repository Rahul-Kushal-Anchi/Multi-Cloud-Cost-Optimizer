terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# S3 bucket for cost lake (placeholder simple bucket)
resource "aws_s3_bucket" "costlake" {
  bucket = "costlake-${var.env}-${random_id.rand.hex}"
  force_destroy = true
}

resource "random_id" "rand" {
  byte_length = 4
}

# DynamoDB table for daily cost (placeholder minimal)
resource "aws_dynamodb_table" "cost_daily" {
  name         = "cost_daily_${var.env}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"

  attribute {
    name = "pk"
    type = "S"
  }
}

# SNS topic for alerts (placeholder)
resource "aws_sns_topic" "alerts" {
  name = "cost-alerts-${var.env}"
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_etl_role" {
  name = "lambda-etl-cur-parser-${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM policy for Lambda to access S3 and DynamoDB
resource "aws_iam_role_policy" "lambda_etl_policy" {
  name = "lambda-etl-policy-${var.env}"
  role = aws_iam_role.lambda_etl_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.costlake.arn,
          "${aws_s3_bucket.costlake.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.cost_daily.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda function for ETL CUR parser
resource "aws_lambda_function" "etl_aws_cur_parser" {
  filename      = "etl_aws_cur_parser.zip"
  function_name = "etl-aws-cur-parser-${var.env}"
  role          = aws_iam_role.lambda_etl_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512

  environment {
    variables = {
      DATA_LAKE_BUCKET = aws_s3_bucket.costlake.bucket
      DDB_TABLE        = aws_dynamodb_table.cost_daily.name
    }
  }

  source_code_hash = fileexists("etl_aws_cur_parser.zip") ? filebase64sha256("etl_aws_cur_parser.zip") : null
}

# S3 bucket notification permission for Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.etl_aws_cur_parser.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.costlake.arn
}

# S3 bucket notification to trigger Lambda on CSV uploads
resource "aws_s3_bucket_notification" "cur_upload" {
  bucket = aws_s3_bucket.costlake.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.etl_aws_cur_parser.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".csv"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

output "costlake_bucket" {
  value = aws_s3_bucket.costlake.bucket
}

output "lambda_function_name" {
  value = aws_lambda_function.etl_aws_cur_parser.function_name
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.cost_daily.name
}
