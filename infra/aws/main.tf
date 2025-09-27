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

output "costlake_bucket" {
  value = aws_s3_bucket_costlake.bucket
}
