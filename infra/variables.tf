variable "project" { default = "costopt" }
variable "region"  { default = "us-east-1" }
variable "vpc_id" {}
variable "public_subnet_ids" { type = list(string) }
variable "private_subnet_ids" { type = list(string) }
variable "domain" { description = "FQDN like cost.example.com" }
variable "acm_cert_arn" {}
variable "ecr_web_uri" { description = "ECR repo URI for web image (no tag)" }
variable "ecr_api_uri" { description = "ECR repo URI for api image (no tag)" }