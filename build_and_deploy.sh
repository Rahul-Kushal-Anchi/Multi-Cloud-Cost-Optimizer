#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 Building and Deploying AWS Cost Optimizer                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory and ensure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-899156640791}"
ECR_WEB_REPO="aws-cost-optimizer-web"
ECR_API_REPO="aws-cost-optimizer-api"
ECS_CLUSTER="aws-cost-optimizer-dev-cluster"
ECS_WEB_SERVICE="aws-cost-optimizer-dev-web"
ECS_API_SERVICE="aws-cost-optimizer-dev-api"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Region: $AWS_REGION"
echo "  Account: $AWS_ACCOUNT_ID"
echo "  Image Tag: $IMAGE_TAG"
echo "  Working Directory: $(pwd)"
echo ""

# Step 1: Login to ECR
echo -e "${BLUE}Step 1: Authenticating with ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
echo -e "${GREEN}✅ ECR authentication successful${NC}"
echo ""

# Step 2: Build and push Web image
echo -e "${BLUE}Step 2: Building and pushing Web image...${NC}"
if [ ! -d "web-app" ]; then
  echo -e "${YELLOW}⚠️  web-app directory not found in $SCRIPT_DIR${NC}"
  exit 1
fi
cd web-app
docker build --platform linux/amd64 -t $ECR_WEB_REPO:$IMAGE_TAG -t $ECR_WEB_REPO:latest .
docker tag $ECR_WEB_REPO:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_WEB_REPO:$IMAGE_TAG
docker tag $ECR_WEB_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_WEB_REPO:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_WEB_REPO:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_WEB_REPO:latest
cd "$SCRIPT_DIR"
echo -e "${GREEN}✅ Web image pushed to ECR${NC}"
echo ""

# Step 3: Build and push API image
echo -e "${BLUE}Step 3: Building and pushing API image...${NC}"
if [ ! -d "api" ]; then
  echo -e "${YELLOW}⚠️  api directory not found in $SCRIPT_DIR${NC}"
  exit 1
fi
cd api
docker build --platform linux/amd64 -t $ECR_API_REPO:$IMAGE_TAG -t $ECR_API_REPO:latest .
docker tag $ECR_API_REPO:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_API_REPO:$IMAGE_TAG
docker tag $ECR_API_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_API_REPO:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_API_REPO:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_API_REPO:latest
cd "$SCRIPT_DIR"
echo -e "${GREEN}✅ API image pushed to ECR${NC}"
echo ""

# Step 4: Update ECS services
echo -e "${BLUE}Step 4: Updating ECS services...${NC}"
echo "  Updating Web service..."
aws ecs update-service \
  --cluster $ECS_CLUSTER \
  --service $ECS_WEB_SERVICE \
  --force-new-deployment \
  --region $AWS_REGION > /dev/null

echo "  Updating API service..."
aws ecs update-service \
  --cluster $ECS_CLUSTER \
  --service $ECS_API_SERVICE \
  --force-new-deployment \
  --region $AWS_REGION > /dev/null

echo -e "${GREEN}✅ ECS services updated${NC}"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Deployment Complete!                                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Services are updating. Check status with:"
echo "  aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_WEB_SERVICE $ECS_API_SERVICE --region $AWS_REGION"

