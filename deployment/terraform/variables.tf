# AWS Cost Optimizer - Terraform Variables
# Variable definitions for production infrastructure

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "aws-cost-optimizer"
}

variable "domain_name" {
  description = "Domain name for the application (optional)"
  type        = string
  default     = ""
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# ECR Configuration
variable "ecr_repository_url" {
  description = "URL of the ECR repository"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

# ECS Configuration
variable "web_cpu" {
  description = "CPU units for web service"
  type        = number
  default     = 256
}

variable "web_memory" {
  description = "Memory for web service"
  type        = number
  default     = 512
}

variable "web_desired_count" {
  description = "Desired number of web service instances"
  type        = number
  default     = 2
}

variable "web_min_capacity" {
  description = "Minimum capacity for web service autoscaling"
  type        = number
  default     = 1
}

variable "web_max_capacity" {
  description = "Maximum capacity for web service autoscaling"
  type        = number
  default     = 10
}

variable "api_cpu" {
  description = "CPU units for API service"
  type        = number
  default     = 512
}

variable "api_memory" {
  description = "Memory for API service"
  type        = number
  default     = 1024
}

variable "api_desired_count" {
  description = "Desired number of API service instances"
  type        = number
  default     = 2
}

variable "api_min_capacity" {
  description = "Minimum capacity for API service autoscaling"
  type        = number
  default     = 1
}

variable "api_max_capacity" {
  description = "Maximum capacity for API service autoscaling"
  type        = number
  default     = 20
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for RDS"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "awscostoptimizer"
}

variable "db_username" {
  description = "Username for the database"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Password for the database"
  type        = string
  sensitive   = true
}

# Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

# Logging Configuration
variable "log_retention_days" {
  description = "Number of days to retain logs"
  type        = number
  default     = 30
}

# Security Configuration
variable "api_secret_key" {
  description = "Secret key for API authentication"
  type        = string
  sensitive   = true
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable detailed monitoring"
  type        = bool
  default     = true
}

variable "monitoring_email" {
  description = "Email for monitoring alerts"
  type        = string
  default     = ""
}

# Cost Optimization
variable "enable_spot_instances" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = false
}

variable "reserved_instance_plan" {
  description = "Reserved instance plan (1year, 3year)"
  type        = string
  default     = "1year"
  validation {
    condition     = contains(["1year", "3year"], var.reserved_instance_plan)
    error_message = "Reserved instance plan must be either '1year' or '3year'."
  }
}

# Backup Configuration
variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Backup window for RDS"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Maintenance window for RDS"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

# SSL/TLS Configuration
variable "certificate_arn" {
  description = "ARN of the SSL certificate"
  type        = string
  default     = ""
}

variable "enable_ssl" {
  description = "Enable SSL/TLS"
  type        = bool
  default     = true
}

# Performance Configuration
variable "enable_performance_insights" {
  description = "Enable RDS Performance Insights"
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "Performance Insights retention period in days"
  type        = number
  default     = 7
}

# Security Configuration
variable "enable_encryption" {
  description = "Enable encryption at rest"
  type        = bool
  default     = true
}

variable "enable_network_encryption" {
  description = "Enable network encryption"
  type        = bool
  default     = true
}

# Compliance Configuration
variable "compliance_standard" {
  description = "Compliance standard (SOC2, HIPAA, PCI)"
  type        = string
  default     = "SOC2"
  validation {
    condition     = contains(["SOC2", "HIPAA", "PCI"], var.compliance_standard)
    error_message = "Compliance standard must be one of: SOC2, HIPAA, PCI."
  }
}

# Disaster Recovery
variable "enable_multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = true
}

variable "enable_cross_region_backup" {
  description = "Enable cross-region backup"
  type        = bool
  default     = false
}

variable "backup_region" {
  description = "Region for cross-region backup"
  type        = string
  default     = "us-west-2"
}

# Cost Management
variable "budget_limit" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 1000
}

variable "budget_alert_thresholds" {
  description = "Budget alert thresholds as percentages"
  type        = list(number)
  default     = [50, 80, 100]
}

# Feature Flags
variable "enable_advanced_monitoring" {
  description = "Enable advanced monitoring features"
  type        = bool
  default     = false
}

variable "enable_auto_scaling" {
  description = "Enable auto-scaling"
  type        = bool
  default     = true
}

variable "enable_load_testing" {
  description = "Enable load testing"
  type        = bool
  default     = false
}

# Development Configuration
variable "enable_debug_mode" {
  description = "Enable debug mode"
  type        = bool
  default     = false
}

variable "enable_development_tools" {
  description = "Enable development tools"
  type        = bool
  default     = false
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
