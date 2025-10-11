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

# SQS Queue for event processing
resource "aws_sqs_queue" "cur_processing_queue" {
  name = "cur-processing-queue-${var.env}"
  
  visibility_timeout_seconds = 300
  message_retention_seconds  = 1209600  # 14 days
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.cur_processing_dlq.arn
    maxReceiveCount     = 3
  })
}

# Dead Letter Queue for failed messages
resource "aws_sqs_queue" "cur_processing_dlq" {
  name = "cur-processing-dlq-${var.env}"
  
  message_retention_seconds = 1209600  # 14 days
}

# EventBridge Custom Event Bus
resource "aws_cloudwatch_event_bus" "cost_optimizer_bus" {
  name = "cost-optimizer-event-bus-${var.env}"
}

# EventBridge Rule for S3 Object Created events
resource "aws_cloudwatch_event_rule" "s3_cur_upload" {
  name           = "s3-cur-upload-${var.env}"
  event_bus_name = aws_cloudwatch_event_bus.cost_optimizer_bus.name

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["Object Created"]
    detail = {
      bucket = {
        name = [aws_s3_bucket.costlake.bucket]
      }
      object = {
        key = [{
          suffix = ".csv"
        }]
      }
    }
  })
}

# EventBridge Target to send events to SQS
resource "aws_cloudwatch_event_target" "s3_to_sqs" {
  rule           = aws_cloudwatch_event_rule.s3_cur_upload.name
  event_bus_name = aws_cloudwatch_event_bus.cost_optimizer_bus.name
  target_id      = "S3ToSQSTarget"
  arn            = aws_sqs_queue.cur_processing_queue.arn
  role_arn       = aws_iam_role.eventbridge_sqs_role.arn
}

# IAM role for EventBridge to send messages to SQS
resource "aws_iam_role" "eventbridge_sqs_role" {
  name = "eventbridge-sqs-role-${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "events.amazonaws.com"
      }
    }]
  })
}

# IAM policy for EventBridge to send messages to SQS
resource "aws_iam_role_policy" "eventbridge_sqs_policy" {
  name = "eventbridge-sqs-policy-${var.env}"
  role = aws_iam_role.eventbridge_sqs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "sqs:SendMessage"
      ]
      Resource = aws_sqs_queue.cur_processing_queue.arn
    }]
  })
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

# IAM policy for Lambda to access S3, DynamoDB, SQS, and SNS
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
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.cur_processing_queue.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.alerts.arn
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
      SNS_TOPIC_ARN    = aws_sns_topic.alerts.arn
    }
  }

  source_code_hash = fileexists("etl_aws_cur_parser.zip") ? filebase64sha256("etl_aws_cur_parser.zip") : null
}

# Event source mapping for Lambda to consume from SQS
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.cur_processing_queue.arn
  function_name    = aws_lambda_function.etl_aws_cur_parser.function_name
  batch_size       = 1
  enabled          = true
}

# S3 bucket notification to send events to EventBridge
resource "aws_s3_bucket_notification" "cur_upload" {
  bucket = aws_s3_bucket.costlake.id

  eventbridge = true
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

output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "eventbridge_bus_name" {
  value = aws_cloudwatch_event_bus.cost_optimizer_bus.name
}
