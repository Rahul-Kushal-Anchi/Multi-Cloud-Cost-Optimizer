variable "region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "cur_bucket_prefix" {
  description = "Prefix for CUR S3 bucket name"
  type        = string
  default     = "cost-optimizer-cur-"
}

variable "cur_prefix" {
  description = "S3 prefix/path for CUR reports"
  type        = string
  default     = "cur/"
}

variable "cur_report_name" {
  description = "Name for the Cost and Usage Report"
  type        = string
  default     = "cost-optimizer-cur"
}

variable "athena_database_name" {
  description = "Name for the Athena/Glue database"
  type        = string
  default     = "aws_billing"
}

variable "athena_workgroup_name" {
  description = "Name for the Athena workgroup (must not be 'primary' - it's a reserved default workgroup)"
  type        = string
  default     = "cost-optimizer-workgroup"
}

variable "athena_results_bucket_prefix" {
  description = "Prefix for Athena results S3 bucket name"
  type        = string
  default     = "cost-optimizer-athena-results-"
}

variable "athena_results_prefix" {
  description = "S3 prefix for Athena query results"
  type        = string
  default     = "athena-results/"
}

variable "enable_result_cleanup" {
  description = "Enable lifecycle policy to delete old Athena query results"
  type        = bool
  default     = true
}

variable "result_retention_days" {
  description = "Number of days to retain Athena query results before deletion"
  type        = number
  default     = 30
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "production"
    Project     = "cost-optimizer"
  }
}
