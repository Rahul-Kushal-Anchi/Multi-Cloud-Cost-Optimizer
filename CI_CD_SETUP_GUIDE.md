# CI/CD Pipeline Setup Guide

This guide explains how to set up and use the automated CI/CD pipeline for the AWS Cost Optimizer application.

## 🚀 Pipeline Overview

The CI/CD pipeline consists of 4 main workflows:

1. **Deploy** (`deploy.yml`) - Main deployment pipeline
2. **Security** (`security.yml`) - Security scanning and code quality
3. **Infrastructure** (`infrastructure.yml`) - Terraform infrastructure management
4. **Monitoring** (`monitoring.yml`) - CloudWatch and X-Ray setup

## 📋 Prerequisites

### GitHub Secrets Required

Add these secrets to your GitHub repository:

```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

### AWS Permissions Required

The AWS credentials need these permissions:
- ECR (Elastic Container Registry)
- ECS (Elastic Container Service)
- CloudWatch
- X-Ray
- IAM (for task definitions)
- VPC (for networking)

## 🔧 Pipeline Workflows

### 1. Deploy Workflow (`deploy.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch

**What it does:**
- Runs tests (Python and Node.js)
- Builds Docker images for AMD64
- Pushes images to ECR
- Deploys to ECS Fargate
- Updates task definitions

**Steps:**
1. **Test Phase:**
   - Python API tests with pytest
   - Node.js web app tests
   - Code coverage reporting

2. **Build Phase:**
   - Builds web application Docker image
   - Builds API application Docker image
   - Tags with commit SHA and `latest`

3. **Deploy Phase:**
   - Updates ECS task definitions
   - Deploys to ECS services
   - Waits for service stability

### 2. Security Workflow (`security.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests
- Weekly schedule (Mondays at 2 AM)

**What it does:**
- Security vulnerability scanning
- Code quality checks
- Docker image security scanning

**Security Tools:**
- **Bandit** - Python security linting
- **Safety** - Python dependency vulnerability scanning
- **Semgrep** - Static analysis security scanning
- **Trivy** - Container vulnerability scanning
- **npm audit** - Node.js dependency scanning

### 3. Infrastructure Workflow (`infrastructure.yml`)

**Triggers:**
- Changes to `deployment/terraform/` files
- Manual workflow dispatch

**What it does:**
- Terraform plan/apply/destroy
- Infrastructure validation
- Environment-specific deployments

**Environments:**
- `development` (default)
- `staging`
- `production`

**Actions:**
- `plan` - Shows what will be changed
- `apply` - Applies infrastructure changes
- `destroy` - Destroys infrastructure (use with caution!)

### 4. Monitoring Workflow (`monitoring.yml`)

**Triggers:**
- Changes to `deployment/monitoring/` files
- Manual workflow dispatch

**What it does:**
- Sets up CloudWatch dashboards
- Creates CloudWatch alarms
- Configures log groups
- Sets up X-Ray tracing

## 🎯 Usage Examples

### Deploying Code Changes

```bash
# 1. Make your changes
git add .
git commit -m "Add new feature"
git push origin main

# 2. Pipeline automatically:
#    - Runs tests
#    - Builds Docker images
#    - Deploys to ECS
#    - Updates services
```

### Manual Infrastructure Deployment

1. Go to GitHub Actions
2. Select "Infrastructure Management"
3. Click "Run workflow"
4. Choose environment and action

### Setting Up Monitoring

1. Go to GitHub Actions
2. Select "Monitoring and Alerting Setup"
3. Click "Run workflow"
4. Choose "setup" action

## 📊 Monitoring Dashboard

After running the monitoring setup, you'll have:

### CloudWatch Dashboard
- **URL**: https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=AWS-Cost-Optimizer-Dashboard
- **Metrics**: CPU, Memory, ALB metrics, ECS tasks

### CloudWatch Alarms
- High CPU utilization (>80%)
- High memory utilization (>85%)
- High 5xx error rate (>10 errors)

### X-Ray Tracing
- **URL**: https://us-east-1.console.aws.amazon.com/xray/home?region=us-east-1#/traces
- **Sampling**: 10% of requests
- **Groups**: Organized by service

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Docker build logs
   - Verify Dockerfile syntax
   - Ensure all dependencies are installed

2. **Deployment Failures**
   - Check ECS service logs
   - Verify task definition
   - Check security group rules

3. **Test Failures**
   - Run tests locally first
   - Check test dependencies
   - Verify test configuration

### Debug Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster aws-cost-optimizer-dev-cluster --services aws-cost-optimizer-dev-api aws-cost-optimizer-dev-web

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/ecs/aws-cost-optimizer-dev"

# Check ECR images
aws ecr describe-images --repository-name aws-cost-optimizer-api
```

## 🚨 Security Best Practices

1. **Secrets Management**
   - Never commit AWS credentials
   - Use GitHub Secrets
   - Rotate credentials regularly

2. **Image Security**
   - Scan images for vulnerabilities
   - Use minimal base images
   - Keep dependencies updated

3. **Access Control**
   - Use least privilege IAM policies
   - Enable MFA for AWS accounts
   - Monitor access logs

## 📈 Performance Optimization

### Build Optimization
- Use multi-stage Docker builds
- Cache dependencies
- Parallel job execution

### Deployment Optimization
- Blue-green deployments
- Rolling updates
- Health checks

### Monitoring Optimization
- Set appropriate alarm thresholds
- Use custom metrics
- Implement alerting

## 🔄 Rollback Procedures

### Code Rollback
```bash
# Revert to previous commit
git revert HEAD
git push origin main
```

### Infrastructure Rollback
1. Go to Infrastructure Management workflow
2. Run with previous Terraform state
3. Or manually revert changes

### Service Rollback
```bash
# Update service to previous task definition
aws ecs update-service --cluster aws-cost-optimizer-dev-cluster --service aws-cost-optimizer-dev-api --task-definition aws-cost-optimizer-dev-api:previous-revision
```

## 📞 Support

For issues with the CI/CD pipeline:

1. Check GitHub Actions logs
2. Review AWS CloudWatch logs
3. Verify AWS permissions
4. Check service health

## 🎉 Success Indicators

Your CI/CD pipeline is working correctly when:

- ✅ All tests pass
- ✅ Docker images build successfully
- ✅ ECS services deploy without errors
- ✅ Health checks pass
- ✅ Monitoring dashboards show data
- ✅ Alarms are configured properly

---

**Next Steps:**
- Set up Slack/email notifications for deployments
- Configure production environment
- Add performance testing
- Implement blue-green deployments
