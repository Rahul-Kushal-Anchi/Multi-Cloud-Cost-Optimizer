# AWS Cost Optimizer - Staging Environment Variables
# Staging configuration for Terraform deployment

# Environment Configuration
environment = "staging"
aws_region = "us-east-1"
project_name = "aws-cost-optimizer"

# Domain Configuration
domain_name = "staging.awscostoptimizer.com"
certificate_arn = ""  # Will be set after SSL certificate is created

# VPC Configuration
vpc_cidr = "10.1.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]
private_subnet_cidrs = ["10.1.1.0/24", "10.1.2.0/24"]
public_subnet_cidrs = ["10.1.101.0/24", "10.1.102.0/24"]

# ECR Configuration
ecr_repository_url = "899156640791.dkr.ecr.us-east-1.amazonaws.com/aws-cost-optimizer"
image_tag = "staging"

# ECS Configuration - Web Service
web_cpu = 256
web_memory = 512
web_desired_count = 2
web_min_capacity = 1
web_max_capacity = 10

# ECS Configuration - API Service
api_cpu = 512
api_memory = 1024
api_desired_count = 2
api_min_capacity = 1
api_max_capacity = 15

# Database Configuration
db_instance_class = "db.t3.small"
db_allocated_storage = 50
db_max_allocated_storage = 200
db_name = "awscostoptimizer_staging"
db_username = "postgres"
db_password = "StagingPassword123!"

# Redis Configuration
redis_node_type = "cache.t3.micro"
redis_num_cache_nodes = 1

# Logging Configuration
log_retention_days = 30

# Security Configuration
api_secret_key = "staging-secret-key-change-this"

# Monitoring Configuration
enable_monitoring = true
monitoring_email = "staging@awscostoptimizer.com"

# Cost Optimization
enable_spot_instances = true
reserved_instance_plan = "1year"

# Backup Configuration
backup_retention_days = 7
backup_window = "03:00-04:00"
maintenance_window = "sun:04:00-sun:05:00"

# SSL/TLS Configuration
enable_ssl = true
certificate_arn = ""

# Performance Configuration
enable_performance_insights = true
performance_insights_retention_period = 7

# Security Configuration
enable_encryption = true
enable_network_encryption = true

# Compliance Configuration
compliance_standard = "SOC2"

# Disaster Recovery
enable_multi_az = false
enable_cross_region_backup = false
backup_region = "us-west-2"

# Cost Management
budget_limit = 1000
budget_alert_thresholds = [50, 80, 100]

# Feature Flags
enable_advanced_monitoring = false
enable_auto_scaling = true
enable_load_testing = true

# Development Configuration
enable_debug_mode = true
enable_development_tools = true

# Additional Tags
additional_tags = {
  "Environment" = "staging"
  "Project" = "aws-cost-optimizer"
  "Owner" = "engineering-team"
  "CostCenter" = "engineering"
  "Backup" = "optional"
  "Monitoring" = "enabled"
}
