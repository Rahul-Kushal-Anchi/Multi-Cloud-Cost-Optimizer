# AWS Cost Optimizer - Development Environment Variables
# Development configuration for Terraform deployment

# Environment Configuration
environment = "dev"
aws_region = "us-east-1"
project_name = "aws-cost-optimizer"

# Domain Configuration
domain_name = "dev.awscostoptimizer.com"
certificate_arn = ""  # Will be set after SSL certificate is created

# VPC Configuration
vpc_cidr = "10.2.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]
private_subnet_cidrs = ["10.2.1.0/24", "10.2.2.0/24"]
public_subnet_cidrs = ["10.2.101.0/24", "10.2.102.0/24"]

# ECR Configuration
ecr_repository_url = "899156640791.dkr.ecr.us-east-1.amazonaws.com/aws-cost-optimizer"
image_tag = "dev"

# ECS Configuration - Web Service
web_cpu = 256
web_memory = 512
web_desired_count = 1
web_min_capacity = 1
web_max_capacity = 5

# ECS Configuration - API Service
api_cpu = 256
api_memory = 512
api_desired_count = 1
api_min_capacity = 1
api_max_capacity = 5

# Database Configuration
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
db_max_allocated_storage = 100
db_name = "awscostoptimizer_dev"
db_username = "postgres"
db_password = "DevPassword123!"

# Redis Configuration
redis_node_type = "cache.t3.micro"
redis_num_cache_nodes = 1

# Logging Configuration
log_retention_days = 7

# Security Configuration
api_secret_key = "dev-secret-key-change-this"

# Monitoring Configuration
enable_monitoring = false
monitoring_email = "dev@awscostoptimizer.com"

# Cost Optimization
enable_spot_instances = true
reserved_instance_plan = "1year"

# Backup Configuration
backup_retention_days = 1
backup_window = "03:00-04:00"
maintenance_window = "sun:04:00-sun:05:00"

# SSL/TLS Configuration
enable_ssl = false

# Performance Configuration
enable_performance_insights = false
performance_insights_retention_period = 1

# Security Configuration
enable_encryption = true
enable_network_encryption = false

# Compliance Configuration
compliance_standard = "SOC2"

# Disaster Recovery
enable_multi_az = false
enable_cross_region_backup = false
backup_region = "us-west-2"

# Cost Management
budget_limit = 200
budget_alert_thresholds = [50, 80, 100]

# Feature Flags
enable_advanced_monitoring = false
enable_auto_scaling = false
enable_load_testing = false

# Development Configuration
enable_debug_mode = true
enable_development_tools = true

# Additional Tags
additional_tags = {
  "Environment" = "dev"
  "Project" = "aws-cost-optimizer"
  "Owner" = "engineering-team"
  "CostCenter" = "engineering"
  "Backup" = "disabled"
  "Monitoring" = "disabled"
}
