# Deploy AWS Cost Optimizer Workflow - Failure Explanation

## 🔍 **Why It's Failing**

### **Error Message:**
```
Credentials could not be loaded, please check your action inputs: 
Could not load credentials from any providers
```

### **Root Cause:**
The workflow is trying to authenticate with AWS using GitHub Secrets, but **the required secrets are not configured** in your GitHub repository.

---

## 📋 **What the Workflow Needs**

The `deploy.yml` workflow requires **3 GitHub Secrets** to be configured:

### **Required Secrets:**

1. **`AWS_ROLE_ARN`** ⚠️ **MISSING**
   - **Purpose:** IAM Role ARN for OIDC authentication
   - **Format:** `arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME`
   - **Used in:** `aws-actions/configure-aws-credentials@v4` step
   - **Why it's needed:** GitHub Actions uses OIDC to assume an AWS IAM role securely

2. **`ECR_WEB_URI`** ⚠️ **MISSING**
   - **Purpose:** ECR repository URI for web application Docker image
   - **Format:** `ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/REPOSITORY_NAME`
   - **Example:** `123456789012.dkr.ecr.us-east-1.amazonaws.com/aws-cost-optimizer-web`
   - **Used in:** Docker build and push steps

3. **`ECR_API_URI`** ⚠️ **MISSING**
   - **Purpose:** ECR repository URI for API Docker image
   - **Format:** `ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/REPOSITORY_NAME`
   - **Example:** `123456789012.dkr.ecr.us-east-1.amazonaws.com/aws-cost-optimizer-api`
   - **Used in:** Docker build and push steps

---

## 🔧 **How to Fix It**

### **Step 1: Set Up AWS IAM Role for OIDC**

1. **Create IAM Role:**
   ```bash
   # Create trust policy for GitHub OIDC
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
           },
           "StringLike": {
             "token.actions.githubusercontent.com:sub": "repo:Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer:*"
           }
         }
       }
     ]
   }
   ```

2. **Attach Permissions:**
   - ECR: `AmazonEC2ContainerRegistryFullAccess`
   - ECS: `AmazonECS_FullAccess`
   - Or create custom policy with minimal permissions

3. **Note the Role ARN:**
   - Format: `arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME`

### **Step 2: Create ECR Repositories**

```bash
# Create ECR repositories
aws ecr create-repository --repository-name aws-cost-optimizer-web --region us-east-1
aws ecr create-repository --repository-name aws-cost-optimizer-api --region us-east-1

# Get repository URIs
aws ecr describe-repositories --repository-names aws-cost-optimizer-web --region us-east-1 --query 'repositories[0].repositoryUri'
aws ecr describe-repositories --repository-names aws-cost-optimizer-api --region us-east-1 --query 'repositories[0].repositoryUri'
```

### **Step 3: Configure GitHub Secrets**

1. **Go to GitHub Repository Settings:**
   - Navigate to: `https://github.com/Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer/settings/secrets/actions`

2. **Add Each Secret:**
   - Click **"New repository secret"**
   - Add `AWS_ROLE_ARN` with your IAM role ARN
   - Add `ECR_WEB_URI` with your web ECR repository URI
   - Add `ECR_API_URI` with your API ECR repository URI

---

## 📊 **Workflow Steps Breakdown**

The workflow performs these steps:

1. ✅ **Checkout code** - Works fine
2. ❌ **Configure AWS credentials** - **FAILS HERE** (missing `AWS_ROLE_ARN`)
3. ⏸️ **ECR login** - Never reached
4. ⏸️ **Build & push web image** - Never reached (needs `ECR_WEB_URI`)
5. ⏸️ **Build & push API image** - Never reached (needs `ECR_API_URI`)
6. ⏸️ **Force ECS deployment** - Never reached (needs ECS cluster/services)

---

## ✅ **What Happens After Configuration**

Once all secrets are configured:

1. ✅ Workflow authenticates with AWS using OIDC
2. ✅ Logs into ECR
3. ✅ Builds Docker images
4. ✅ Pushes images to ECR
5. ✅ Triggers ECS service updates
6. ✅ New containers deploy automatically

---

## 🎯 **Current Status**

| Component | Status | Action Needed |
|-----------|--------|---------------|
| Workflow Code | ✅ Valid | None |
| AWS IAM Role | ❌ Missing | Create OIDC role |
| GitHub Secret: AWS_ROLE_ARN | ❌ Missing | Add secret |
| GitHub Secret: ECR_WEB_URI | ❌ Missing | Add secret |
| GitHub Secret: ECR_API_URI | ❌ Missing | Add secret |
| ECR Repositories | ❌ Missing | Create repositories |
| ECS Cluster | ⚠️ Unknown | Verify exists |
| ECS Services | ⚠️ Unknown | Verify exist |

---

## 💡 **Quick Fix Options**

### **Option 1: Disable Deployment Workflow (Temporary)**
If you don't need automatic deployment right now, you can:
- Comment out the workflow trigger
- Or add a condition to skip if secrets are missing

### **Option 2: Set Up Full AWS Infrastructure**
Follow the steps above to configure everything properly.

### **Option 3: Use Manual Deployment**
Deploy manually using AWS CLI or console until CI/CD is configured.

---

## 📝 **Summary**

**The workflow is failing because:**
- ❌ GitHub Secrets are not configured
- ❌ AWS IAM Role for OIDC doesn't exist
- ❌ ECR repositories may not exist

**This is expected behavior** - the workflow is correctly detecting that AWS credentials are missing and failing safely rather than attempting to deploy without proper authentication.

**To fix:** Configure the 3 GitHub Secrets listed above, and ensure AWS resources (IAM role, ECR repos, ECS cluster) exist.

---

**Status:** ✅ Workflow code is correct, just needs AWS configuration! 🎯

