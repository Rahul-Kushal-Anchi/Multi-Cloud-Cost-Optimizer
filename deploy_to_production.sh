#!/bin/bash

# 🚀 AWS Cost Optimizer - Production Deployment Script
# This script builds Docker images and deploys to AWS ECS

set -e  # Exit on any error

echo "🚀 Starting Production Deployment..."
echo "=================================="

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="899156640791"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_WEB_REPO="aws-cost-optimizer-web"
ECR_API_REPO="aws-cost-optimizer-api"
ECS_CLUSTER="aws-cost-optimizer-dev-cluster"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop first."
        echo "Visit: https://www.docker.com/products/docker-desktop/"
        exit 1
    fi
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        echo "Run: brew install awscli"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Authenticate with ECR
authenticate_ecr() {
    print_status "Authenticating with ECR..."
    
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
    
    if [ $? -eq 0 ]; then
        print_success "ECR authentication successful"
    else
        print_error "ECR authentication failed"
        exit 1
    fi
}

# Build and push web application
deploy_web_app() {
    print_status "Building and deploying web application..."
    
    # Build web application
    print_status "Building Docker image for web application..."
    docker build -f deployment/docker/Dockerfile.web.simple -t $ECR_WEB_REPO:latest .
    
    if [ $? -ne 0 ]; then
        print_error "Failed to build web application image"
        exit 1
    fi
    
    # Tag for ECR
    docker tag $ECR_WEB_REPO:latest $ECR_REGISTRY/$ECR_WEB_REPO:latest
    
    # Push to ECR
    print_status "Pushing web application to ECR..."
    docker push $ECR_REGISTRY/$ECR_WEB_REPO:latest
    
    if [ $? -eq 0 ]; then
        print_success "Web application deployed to ECR"
    else
        print_error "Failed to push web application to ECR"
        exit 1
    fi
}

# Build and push API application
deploy_api_app() {
    print_status "Building and deploying API application..."
    
    # Build API application
    print_status "Building Docker image for API application..."
    docker build -f deployment/docker/Dockerfile.api.simple -t $ECR_API_REPO:latest .
    
    if [ $? -ne 0 ]; then
        print_error "Failed to build API application image"
        exit 1
    fi
    
    # Tag for ECR
    docker tag $ECR_API_REPO:latest $ECR_REGISTRY/$ECR_API_REPO:latest
    
    # Push to ECR
    print_status "Pushing API application to ECR..."
    docker push $ECR_REGISTRY/$ECR_API_REPO:latest
    
    if [ $? -eq 0 ]; then
        print_success "API application deployed to ECR"
    else
        print_error "Failed to push API application to ECR"
        exit 1
    fi
}

# Update ECS services
update_ecs_services() {
    print_status "Updating ECS services..."
    
    # Force update web service
    print_status "Updating web service..."
    aws ecs update-service --cluster $ECS_CLUSTER --service aws-cost-optimizer-dev-web --force-new-deployment
    
    if [ $? -eq 0 ]; then
        print_success "Web service update initiated"
    else
        print_error "Failed to update web service"
        exit 1
    fi
    
    # Force update API service
    print_status "Updating API service..."
    aws ecs update-service --cluster $ECS_CLUSTER --service aws-cost-optimizer-dev-api --force-new-deployment
    
    if [ $? -eq 0 ]; then
        print_success "API service update initiated"
    else
        print_error "Failed to update API service"
        exit 1
    fi
}

# Wait for services to be stable
wait_for_services() {
    print_status "Waiting for services to be stable..."
    
    # Wait for web service
    print_status "Waiting for web service to be stable..."
    aws ecs wait services-stable --cluster $ECS_CLUSTER --services aws-cost-optimizer-dev-web
    
    if [ $? -eq 0 ]; then
        print_success "Web service is stable"
    else
        print_warning "Web service may not be stable yet"
    fi
    
    # Wait for API service
    print_status "Waiting for API service to be stable..."
    aws ecs wait services-stable --cluster $ECS_CLUSTER --services aws-cost-optimizer-dev-api
    
    if [ $? -eq 0 ]; then
        print_success "API service is stable"
    else
        print_warning "API service may not be stable yet"
    fi
}

# Test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Test web application
    print_status "Testing web application..."
    if curl -I https://dev.awscostoptimizer.com &> /dev/null; then
        print_success "Web application is accessible"
    else
        print_warning "Web application may not be ready yet"
    fi
    
    # Test API
    print_status "Testing API..."
    if curl -I https://api.dev.awscostoptimizer.com/health &> /dev/null; then
        print_success "API is accessible"
    else
        print_warning "API may not be ready yet"
    fi
}

# Main deployment function
main() {
    echo ""
    print_status "Starting AWS Cost Optimizer Production Deployment"
    echo "========================================================"
    echo ""
    
    # Step 1: Check prerequisites
    check_prerequisites
    echo ""
    
    # Step 2: Authenticate with ECR
    authenticate_ecr
    echo ""
    
    # Step 3: Deploy web application
    deploy_web_app
    echo ""
    
    # Step 4: Deploy API application
    deploy_api_app
    echo ""
    
    # Step 5: Update ECS services
    update_ecs_services
    echo ""
    
    # Step 6: Wait for services to be stable
    wait_for_services
    echo ""
    
    # Step 7: Test deployment
    test_deployment
    echo ""
    
    # Final status
    echo "========================================================"
    print_success "Deployment completed!"
    echo ""
    echo "🌐 Application URLs:"
    echo "• Web App: https://dev.awscostoptimizer.com"
    echo "• API: https://api.dev.awscostoptimizer.com"
    echo ""
    echo "📊 Monitor your deployment:"
    echo "• ECS Console: https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/$ECS_CLUSTER/services"
    echo "• CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups"
    echo ""
    print_status "Deployment script completed successfully!"
}

# Run main function
main "$@"
