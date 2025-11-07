terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.region
}

# Random suffix for resource names
resource "random_id" "suffix" {
  byte_length = 4
}

# ============================================================================
# S3 Bucket for CUR Reports
# ============================================================================

resource "aws_s3_bucket" "cur_reports" {
  bucket = "${var.cur_bucket_prefix}${random_id.suffix.hex}"
  
  tags = merge(
    var.tags,
    {
      Name        = "CUR Reports Bucket"
      Purpose     = "AWS Cost and Usage Reports"
      ManagedBy   = "Terraform"
    }
  )
}

resource "aws_s3_bucket_versioning" "cur_reports" {
  bucket = aws_s3_bucket.cur_reports.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cur_reports" {
  bucket = aws_s3_bucket.cur_reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "cur_reports" {
  bucket = aws_s3_bucket.cur_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM policy document for CUR service to write to bucket
data "aws_iam_policy_document" "cur_reports_bucket_policy" {
  statement {
    sid    = "AllowCURWrite"
    effect = "Allow"
    
    principals {
      type        = "Service"
      identifiers = ["billingreports.amazonaws.com"]
    }
    
    actions = [
      "s3:GetBucketAcl",
      "s3:GetBucketPolicy",
      "s3:PutObject",
    ]
    
    resources = [
      aws_s3_bucket.cur_reports.arn,
      "${aws_s3_bucket.cur_reports.arn}/*",
    ]
    
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
    
    condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values   = ["arn:aws:cur:${var.region}::definition/*"]
    }
  }
}

resource "aws_s3_bucket_policy" "cur_reports" {
  bucket = aws_s3_bucket.cur_reports.id
  policy = data.aws_iam_policy_document.cur_reports_bucket_policy.json
}

# ============================================================================
# AWS Cost and Usage Report (CUR)
# ============================================================================

resource "aws_cur_report_definition" "main" {
  report_name                = var.cur_report_name
  time_unit                  = "DAILY"
  format                     = "textORcsv"  # Using CSV format (more compatible)
  compression                = "GZIP"
  additional_schema_elements = ["RESOURCES"]
  s3_bucket                  = aws_s3_bucket.cur_reports.bucket
  s3_prefix                  = var.cur_prefix
  s3_region                  = var.region
  report_versioning          = "OVERWRITE_REPORT"
  
  # Enable Athena integration
  refresh_closed_reports = true
  
  depends_on = [aws_s3_bucket_policy.cur_reports]
}

# ============================================================================
# Glue Database for CUR
# ============================================================================

resource "aws_glue_catalog_database" "cur" {
  name        = var.athena_database_name
  description = "AWS Cost and Usage Reports database"
  
  location_uri = "s3://${aws_s3_bucket.cur_reports.bucket}/${var.cur_prefix}"
  
  parameters = {
    "classification" = "csv"
  }
  
  tags = merge(
    var.tags,
    {
      Name      = "CUR Database"
      ManagedBy = "Terraform"
    }
  )
}

# Note: The Athena table is automatically created by AWS when CUR is delivered
# You can query it after the first report arrives (~24 hours)
# Table name format: cost_and_usage_report_YYYYMMDD (or similar)

# ============================================================================
# Athena Workgroup
# ============================================================================

resource "aws_athena_workgroup" "main" {
  name        = var.athena_workgroup_name
  description = "Workgroup for querying Cost and Usage Reports"
  state       = "ENABLED"
  
  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true
    
    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/${var.athena_results_prefix}"
      
      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }
  
  tags = merge(
    var.tags,
    {
      Name      = "CUR Athena Workgroup"
      ManagedBy = "Terraform"
    }
  )
}

# ============================================================================
# S3 Bucket for Athena Query Results
# ============================================================================

resource "aws_s3_bucket" "athena_results" {
  bucket = "${var.athena_results_bucket_prefix}${random_id.suffix.hex}"
  
  tags = merge(
    var.tags,
    {
      Name        = "Athena Query Results"
      Purpose     = "Athena query output storage"
      ManagedBy   = "Terraform"
    }
  )
}

resource "aws_s3_bucket_server_side_encryption_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy for Athena results (optional cleanup)
resource "aws_s3_bucket_lifecycle_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id

  rule {
    id     = "delete-old-query-results"
    status = var.enable_result_cleanup ? "Enabled" : "Disabled"

    filter {
      prefix = var.athena_results_prefix
    }

    expiration {
      days = var.result_retention_days
    }
  }
}

# ============================================================================
# Data Sources
# ============================================================================

data "aws_caller_identity" "current" {}

# ============================================================================
# Outputs
# ============================================================================

output "cur_bucket" {
  description = "S3 bucket name for CUR reports"
  value       = aws_s3_bucket.cur_reports.bucket
}

output "cur_prefix" {
  description = "S3 prefix for CUR reports"
  value       = var.cur_prefix
}

output "cur_report_name" {
  description = "Name of the Cost and Usage Report"
  value       = aws_cur_report_definition.main.report_name
}

output "athena_database" {
  description = "Athena database name"
  value       = aws_glue_catalog_database.cur.name
}

output "athena_table" {
  description = "Athena table name (auto-created by AWS after first CUR delivery)"
  value       = "cost_and_usage_report_${formatdate("YYYYMMDD", timeadd(timestamp(), "24h"))}"
  
  # Note: Actual table name depends on when CUR is first delivered
  # Check AWS Glue Console or run: aws glue get-tables --database-name <db>
}

output "athena_workgroup" {
  description = "Athena workgroup name"
  value       = aws_athena_workgroup.main.name
}

output "athena_results_bucket" {
  description = "S3 bucket for Athena query results"
  value       = aws_s3_bucket.athena_results.bucket
}

output "athena_results_prefix" {
  description = "S3 prefix for Athena query results"
  value       = var.athena_results_prefix
}

output "region" {
  description = "AWS region"
  value       = var.region
}

# Output all values needed for /api/tenants/connect
output "connection_values" {
  description = "All values needed for connecting to the Cost Optimizer app"
  value = {
    cur_bucket          = aws_s3_bucket.cur_reports.bucket
    cur_prefix          = var.cur_prefix
    athena_db           = aws_glue_catalog_database.cur.name
    athena_table        = "cost_and_usage_report_*"  # Check Glue after CUR delivery
    athena_workgroup    = aws_athena_workgroup.main.name
    athena_results_bucket = aws_s3_bucket.athena_results.bucket
    athena_results_prefix = var.athena_results_prefix
    region              = var.region
  }
}
