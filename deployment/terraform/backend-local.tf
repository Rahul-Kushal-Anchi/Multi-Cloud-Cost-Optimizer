# AWS Cost Optimizer - Local Terraform Backend
# Use local backend for initial deployment, then migrate to S3

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Use local backend for initial deployment
  backend "local" {
    path = "terraform.tfstate"
  }
}
