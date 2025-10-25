# 🚀 Production Deployment Guide

## Overview
This guide covers the complete production deployment of the AWS Cost Optimizer application to AWS using Terraform, ECS Fargate, and ECR.

## ✅ Current Status
- **Infrastructure**: ✅ Deployed successfully
- **ECR Repository**: ✅ Created
- **ECS Cluster**: ✅ Ready
- **RDS Database**: ✅ Running
- **Redis Cache**: ✅ Running
- **Application Load Balancer**: ✅ Active

## 🏗️ Infrastructure Components

### Core Infrastructure
- **VPC**: `vpc-0986410ea5d808a6a`
- **ECS Cluster**: `aws-cost-optimizer-dev-cluster`
- **Application Load Balancer**: `aws-cost-optimizer-dev-alb-2097253605.us-east-1.elb.amazonaws.com`
- **RDS Database**: `aws-cost-optimizer-dev-db.cqfoeyiys9fy.us-east-1.rds.amazonaws.com:5432`
- **Redis Cache**: `master.aws-cost-optimizer-dev-redis.2wffxx.use1.cache.amazonaws.com`

### Application URLs
- **Web Application**: https://dev.awscostoptimizer.com
- **API Endpoint**: https://api.dev.awscostoptimizer.com

## 📋 Prerequisites

### 1. Install Docker Desktop
```bash
# Download and install Docker Desktop for macOS
# Visit: https://www.docker.com/products/docker-desktop/
# Or install via Homebrew:
brew install --cask docker
```

### 2. Install AWS CLI (if not already installed)
```bash
brew install awscli
```

### 3. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

## 🐳 Docker Image Building

### Step 1: Build Web Application Image
```bash
cd /Users/rahulkushalanchi/Downloads/multi-cloud-cost-optimizer

# Build React web application
docker build -f deployment/docker/Dockerfile.web -t aws-cost-optimizer-web:latest .

# Tag for ECR
docker tag aws-cost-optimizer-web:latest 899156640791.dkr.ecr.us-east-1.amazonaws.com/aws-cost-optimizer-web:latest
```

### Step 2: Build API Application Image
```bash
# Build FastAPI backend
docker build -f deployment/docker/Dockerfile.api -t aws-cost-optimizer-api:latest .

# Tag for ECR
docker tag aws-cost-optimizer-api:latest 899156640791.dkr.ecr.us-east-1.amazonaws.com/aws-cost-optimizer-api:latest
```

## 🔐 ECR Authentication and Push

### Step 1: Authenticate with ECR
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 899156640791.dkr.ecr.us-east-1.amazonaws.com
```

### Step 2: Push Images to ECR
```bash
# Push web application
docker push 899156640791.dkr.ecr.us-east-1.amazonaws.com/aws-cost-optimizer-web:latest

# Push API application
docker push 899156640791.dkr.ecr.us-east-1.amazonaws.com/aws-cost-optimizer-api:latest
```

## 🚀 ECS Service Update

### Step 1: Update ECS Task Definitions
```bash
cd deployment/terraform

# Update task definitions with ECR image URIs
terraform apply -var-file=environments/development.tfvars -auto-approve
```

### Step 2: Force ECS Service Update
```bash
# Force update of ECS services to use new images
aws ecs update-service --cluster aws-cost-optimizer-dev-cluster --service aws-cost-optimizer-dev-web --force-new-deployment
aws ecs update-service --cluster aws-cost-optimizer-dev-cluster --service aws-cost-optimizer-dev-api --force-new-deployment
```

## 🔍 Verification

### Step 1: Check ECS Service Status
```bash
# Check web service
aws ecs describe-services --cluster aws-cost-optimizer-dev-cluster --services aws-cost-optimizer-dev-web

# Check API service
aws ecs describe-services --cluster aws-cost-optimizer-dev-cluster --services aws-cost-optimizer-dev-api
```

### Step 2: Test Application Endpoints
```bash
# Test web application
curl -I https://dev.awscostoptimizer.com

# Test API health endpoint
curl -I https://api.dev.awscostoptimizer.com/health
```

## 🔧 CI/CD Pipeline Setup

### Step 1: Configure GitHub Actions
The CI/CD pipeline is already configured in `deployment/ci-cd/github-actions.yml`. To activate:

1. Go to your GitHub repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `ECR_REGISTRY`: `899156640791.dkr.ecr.us-east-1.amazonaws.com`
   - `ECR_REPOSITORY_WEB`: `aws-cost-optimizer-web`
   - `ECR_REPOSITORY_API`: `aws-cost-optimizer-api`

### Step 2: Enable GitHub Actions
1. Push the code to your repository
2. GitHub Actions will automatically trigger on push to main branch
3. Monitor the workflow in the "Actions" tab

## 📊 Monitoring Setup

### Step 1: CloudWatch Dashboard
```bash
# The CloudWatch dashboard is automatically created
# Access it in the AWS Console under CloudWatch → Dashboards
```

### Step 2: Set up Alerts
```bash
# Run the monitoring setup script
python monitoring_setup.py
```

## 🧪 Testing

### Step 1: Run Integration Tests
```bash
# Test all components
python test_week3_features.py
python test_week4_features.py
python test_week5_features.py
```

### Step 2: Load Testing
```bash
# Run load tests (if available)
# This would test the application under load
```

## 🔒 Security Considerations

### 1. SSL/TLS Certificates
- Currently using HTTP (port 80)
- For production, configure SSL certificates in ACM
- Update ALB listeners to use HTTPS (port 443)

### 2. Database Security
- RDS is in private subnets
- Security groups restrict access
- Encryption at rest is enabled

### 3. Application Security
- Secrets stored in AWS Secrets Manager
- IAM roles with least privilege
- VPC with private/public subnet separation

## 🚨 Troubleshooting

### Common Issues

1. **Docker Build Fails**
   - Ensure Docker Desktop is running
   - Check available disk space
   - Verify Dockerfile syntax

2. **ECR Push Fails**
   - Verify AWS credentials
   - Check ECR repository permissions
   - Ensure ECR login is successful

3. **ECS Service Won't Start**
   - Check task definition
   - Verify image URI is correct
   - Check CloudWatch logs

4. **Application Not Accessible**
   - Verify ALB target group health
   - Check security group rules
   - Ensure Route53 records are correct

### Debugging Commands
```bash
# Check ECS service logs
aws logs describe-log-groups --log-group-name-prefix /ecs/aws-cost-optimizer

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>

# Check RDS status
aws rds describe-db-instances --db-instance-identifier aws-cost-optimizer-dev-db
```

## 📈 Next Steps

1. **SSL Certificate Setup**
   - Request SSL certificate in ACM
   - Update ALB listeners to HTTPS
   - Configure redirect from HTTP to HTTPS

2. **Domain Configuration**
   - Update Route53 records for custom domain
   - Configure DNS settings

3. **Monitoring Enhancement**
   - Set up custom CloudWatch metrics
   - Configure SNS notifications
   - Implement log aggregation

4. **Security Hardening**
   - Enable AWS WAF
   - Configure VPC Flow Logs
   - Set up AWS Config rules

5. **Performance Optimization**
   - Configure CloudFront CDN
   - Implement caching strategies
   - Optimize database queries

## 📞 Support

For issues or questions:
1. Check CloudWatch logs
2. Review ECS service events
3. Verify AWS service status
4. Consult AWS documentation

---

**Deployment Status**: Infrastructure ✅ | Docker Images ⏳ | ECS Services ⏳ | CI/CD ⏳ | Monitoring ⏳
