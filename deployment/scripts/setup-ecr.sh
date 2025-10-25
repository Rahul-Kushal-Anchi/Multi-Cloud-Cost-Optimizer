#!/bin/bash
# AWS Cost Optimizer - ECR Repository Setup Script
# Creates ECR repository and configures Docker authentication

set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY="aws-cost-optimizer"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Setting up ECR repository for AWS Cost Optimizer..."
echo "=================================================="
echo ""
echo "📋 Configuration:"
echo "• AWS Region: $AWS_REGION"
echo "• ECR Repository: $ECR_REPOSITORY"
echo "• AWS Account ID: $AWS_ACCOUNT_ID"
echo ""

# Create ECR repository
echo "🔧 Creating ECR repository..."
aws ecr create-repository \
    --repository-name $ECR_REPOSITORY \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    --tags Key=Project,Value=aws-cost-optimizer Key=Environment,Value=production \
    || echo "Repository already exists"

echo "✅ ECR repository created successfully!"
echo ""

# Configure Docker authentication
echo "🔐 Configuring Docker authentication..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "✅ Docker authentication configured!"
echo ""

# Build and push Docker image
echo "🐳 Building Docker image..."
docker build -f deployment/docker/Dockerfile -t $ECR_REPOSITORY:latest .

echo "🏷️ Tagging Docker image..."
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$(date +%Y%m%d-%H%M%S)

echo "📤 Pushing Docker images to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$(date +%Y%m%d-%H%M%S)

echo "✅ Docker images pushed successfully!"
echo ""

# Update Terraform variables with ECR URL
echo "📝 Updating Terraform variables with ECR URL..."
ECR_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"

# Update production.tfvars
sed -i.bak "s|ecr_repository_url = \".*\"|ecr_repository_url = \"$ECR_URL\"|g" deployment/terraform/environments/production.tfvars
sed -i.bak "s|ecr_repository_url = \".*\"|ecr_repository_url = \"$ECR_URL\"|g" deployment/terraform/environments/staging.tfvars
sed -i.bak "s|ecr_repository_url = \".*\"|ecr_repository_url = \"$ECR_URL\"|g" deployment/terraform/environments/development.tfvars

echo "✅ Terraform variables updated with ECR URL: $ECR_URL"
echo ""

# Display next steps
echo "🎯 NEXT STEPS:"
echo "=============="
echo "1. Run Terraform to deploy infrastructure:"
echo "   cd deployment/terraform"
echo "   terraform init"
echo "   terraform plan -var-file=environments/production.tfvars"
echo "   terraform apply -var-file=environments/production.tfvars"
echo ""
echo "2. Deploy to staging:"
echo "   terraform apply -var-file=environments/staging.tfvars"
echo ""
echo "3. Deploy to development:"
echo "   terraform apply -var-file=environments/development.tfvars"
echo ""
echo "🚀 ECR setup completed successfully!"
