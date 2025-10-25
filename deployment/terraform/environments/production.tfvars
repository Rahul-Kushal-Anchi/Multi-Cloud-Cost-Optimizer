# AWS Cost Optimizer - Production Environment Variables
# Production configuration for Terraform deployment

# Environment Configuration
environment = "production"
aws_region = "us-east-1"
project_name = "aws-cost-optimizer"

# Domain Configuration
domain_name = "awscostoptimizer.com"
certificate_arn = ""  # Will be set after SSL certificate is created

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
public_subnet_cidrs = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

# ECR Configuration
ecr_repository_url = "899156640791.dkr.ecr.us-east-1.amazonaws.com/aws-cost-optimizer"
image_tag = "latest"

# ECS Configuration - Web Service
web_cpu = 512
web_memory = 1024
web_desired_count = 3
web_min_capacity = 2
web_max_capacity = 20

# ECS Configuration - API Service
api_cpu = 1024
api_memory = 2048
api_desired_count = 3
api_min_capacity = 2
api_max_capacity = 30

# Database Configuration
db_instance_class = "db.t3.medium"
db_allocated_storage = 100
db_max_allocated_storage = 1000
db_name = "awscostoptimizer"
db_username = "postgres"
db_password = "SecurePassword123!"  # Change this in production

# Redis Configuration
redis_node_type = "cache.t3.small"
redis_num_cache_nodes = 2

# Logging Configuration
log_retention_days = 90

# Security Configuration
api_secret_key = "your-super-secret-api-key-change-this-in-production"

# Monitoring Configuration
enable_monitoring = true
monitoring_email = "admin@awscostoptimizer.com"

# Cost Optimization
enable_spot_instances = false
reserved_instance_plan = "1year"

# Backup Configuration
backup_retention_days = 30
backup_window = "03:00-04:00"
maintenance_window = "sun:04:00-sun:05:00"

# SSL/TLS Configuration
enable_ssl = true
certificate_arn = ""  # Will be set after certificate creation

# Performance Configuration
enable_performance_insights = true
performance_insights_retention_period = 30

# Security Configuration
enable_encryption = true
enable_network_encryption = true

# Compliance Configuration
compliance_standard = "SOC2"

# Disaster Recovery
enable_multi_az = true
enable_cross_region_backup = true
backup_region = "us-west-2"

# Cost Management
budget_limit = 5000
budget_alert_thresholds = [50, 80, 100]

# Feature Flags
enable_advanced_monitoring = true
enable_auto_scaling = true
enable_load_testing = false

# Development Configuration
enable_debug_mode = false
enable_development_tools = false

# Additional Tags
additional_tags = {
  "Environment" = "production"
  "Project" = "aws-cost-optimizer"
  "Owner" = "engineering-team"
  "CostCenter" = "engineering"
  "Backup" = "required"
  "Monitoring" = "enabled"
}
