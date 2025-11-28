# How to Connect AWS for Anomaly Detection

## 🎯 Current Situation

You have a user account, but AWS isn't connected yet. To use anomaly detection with **REAL data**, you need to:

1. ✅ **You already have a tenant** (created when you signed up)
2. ⏳ **Connect AWS account** to your tenant
3. ⏳ **Configure CUR and Athena** settings

---

## 📋 Step-by-Step: Connect AWS

### **Step 1: Access Connect AWS Page**

1. **Option A: Via Settings**
   - Go to **Settings** page
   - Look for "Connect AWS" or "AWS Connection" section

2. **Option B: Direct Route**
   - Navigate to `/connect-aws` in your browser
   - Or click "Connect AWS" link if available

3. **Option C: Via Admin Panel** (if you're global owner)
   - Go to Admin page
   - Find your tenant
   - Click "Connect AWS" button

---

### **Step 2: Prepare AWS Setup**

Before connecting, you need to set up AWS:

#### **A. Deploy CloudFormation Stack**

1. **In AWS Console:**
   - Go to CloudFormation
   - Create new stack
   - Use template: `cfn/connect-aws-billing.yml` (if available)
   - Or create IAM role manually

2. **What it creates:**
   - IAM Role with read-only access to billing
   - External ID for security
   - Permissions for Athena, CloudWatch, CUR

3. **After deployment, get:**
   - **Role ARN**: `arn:aws:iam::123456789012:role/CostOptimizerAccess`
   - **External ID**: UUID from stack outputs

#### **B. Set Up Cost and Usage Report (CUR)**

1. **In AWS Console:**
   - Go to **Billing** → **Cost and Usage Reports**
   - Create new report (if not exists)
   - Enable **Athena integration**
   - Note the S3 bucket name

2. **Wait for CUR data:**
   - First report takes 24-48 hours
   - After that, daily updates

#### **C. Set Up Athena Database**

1. **In AWS Console:**
   - Go to **Athena**
   - Create database (if CUR integration created it, use that)
   - Note database name and table name

2. **Common names:**
   - Database: `cost_optimizer_cur_db`
   - Table: `cost_optimizer_cur_table`
   - Workgroup: `primary`

---

### **Step 3: Fill in Connection Form**

In the Connect AWS page, enter:

**Required Fields:**
- **AWS Role ARN**: `arn:aws:iam::123456789012:role/CostOptimizerAccess`
- **External ID**: UUID from CloudFormation stack
- **Region**: `us-east-1` (or your region)

**CUR Settings:**
- **CUR Bucket**: S3 bucket where CUR is stored
- **CUR Prefix**: Usually `cur/` or empty

**Athena Settings:**
- **Athena Database**: Database name from Athena
- **Athena Table**: Table name from Athena
- **Athena Workgroup**: Usually `primary`
- **Results Bucket**: S3 bucket for Athena query results
- **Results Prefix**: Usually `athena-results/`

---

### **Step 4: Save Connection**

1. Click **"Save Connection"** or **"Connect AWS"**
2. System will:
   - Test the AWS connection (AssumeRole)
   - Validate credentials
   - Save settings to database

3. **If successful:**
   - You'll see "AWS connection saved successfully!"
   - Redirected to dashboard
   - Can now see real cost data

---

## 🔍 Verify Connection

After connecting, verify:

1. **Check Dashboard:**
   - Go to Dashboard
   - Should show real cost data (not zeros)
   - Charts should populate

2. **Check Settings:**
   - Go to Settings
   - Should show "AWS Connected" status

3. **Test API:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:9000/api/dashboard
   ```
   Should return real cost data

---

## 🚨 Troubleshooting

### **Error: "Cannot AssumeRole"**
- **Check**: Role ARN is correct
- **Check**: External ID matches CloudFormation stack
- **Check**: IAM role trust policy allows your account

### **Error: "No CUR data found"**
- **Check**: CUR is enabled and generating reports
- **Check**: Wait 24-48 hours for first report
- **Check**: S3 bucket path is correct

### **Error: "Athena table not found"**
- **Check**: Database and table names are correct
- **Check**: CUR Athena integration is enabled
- **Check**: Table exists in Athena console

---

## ✅ After Connection

Once AWS is connected:

1. **Real cost data** will flow from CUR → Athena → Your app
2. **Anomaly detection** can train on real historical data
3. **CloudWatch metrics** can be collected
4. **All ML features** will use real data

---

## 🎯 Next Steps

After connecting AWS:

1. ✅ Wait for CUR data (24-48 hours if new)
2. ✅ Verify dashboard shows real costs
3. ✅ Implement anomaly detection model
4. ✅ Train on real historical data (90 days)
5. ✅ Start detecting anomalies in real-time

---

## 💡 Quick Reference

**API Endpoint:** `POST /api/tenants/connect`

**Required Fields:**
- `aws_role_arn`
- `external_id`
- `region`
- `athena_db`
- `athena_table`

**Optional Fields:**
- `cur_bucket`
- `cur_prefix`
- `athena_workgroup`
- `athena_results_bucket`
- `athena_results_prefix`



## 🎯 Current Situation

You have a user account, but AWS isn't connected yet. To use anomaly detection with **REAL data**, you need to:

1. ✅ **You already have a tenant** (created when you signed up)
2. ⏳ **Connect AWS account** to your tenant
3. ⏳ **Configure CUR and Athena** settings

---

## 📋 Step-by-Step: Connect AWS

### **Step 1: Access Connect AWS Page**

1. **Option A: Via Settings**
   - Go to **Settings** page
   - Look for "Connect AWS" or "AWS Connection" section

2. **Option B: Direct Route**
   - Navigate to `/connect-aws` in your browser
   - Or click "Connect AWS" link if available

3. **Option C: Via Admin Panel** (if you're global owner)
   - Go to Admin page
   - Find your tenant
   - Click "Connect AWS" button

---

### **Step 2: Prepare AWS Setup**

Before connecting, you need to set up AWS:

#### **A. Deploy CloudFormation Stack**

1. **In AWS Console:**
   - Go to CloudFormation
   - Create new stack
   - Use template: `cfn/connect-aws-billing.yml` (if available)
   - Or create IAM role manually

2. **What it creates:**
   - IAM Role with read-only access to billing
   - External ID for security
   - Permissions for Athena, CloudWatch, CUR

3. **After deployment, get:**
   - **Role ARN**: `arn:aws:iam::123456789012:role/CostOptimizerAccess`
   - **External ID**: UUID from stack outputs

#### **B. Set Up Cost and Usage Report (CUR)**

1. **In AWS Console:**
   - Go to **Billing** → **Cost and Usage Reports**
   - Create new report (if not exists)
   - Enable **Athena integration**
   - Note the S3 bucket name

2. **Wait for CUR data:**
   - First report takes 24-48 hours
   - After that, daily updates

#### **C. Set Up Athena Database**

1. **In AWS Console:**
   - Go to **Athena**
   - Create database (if CUR integration created it, use that)
   - Note database name and table name

2. **Common names:**
   - Database: `cost_optimizer_cur_db`
   - Table: `cost_optimizer_cur_table`
   - Workgroup: `primary`

---

### **Step 3: Fill in Connection Form**

In the Connect AWS page, enter:

**Required Fields:**
- **AWS Role ARN**: `arn:aws:iam::123456789012:role/CostOptimizerAccess`
- **External ID**: UUID from CloudFormation stack
- **Region**: `us-east-1` (or your region)

**CUR Settings:**
- **CUR Bucket**: S3 bucket where CUR is stored
- **CUR Prefix**: Usually `cur/` or empty

**Athena Settings:**
- **Athena Database**: Database name from Athena
- **Athena Table**: Table name from Athena
- **Athena Workgroup**: Usually `primary`
- **Results Bucket**: S3 bucket for Athena query results
- **Results Prefix**: Usually `athena-results/`

---

### **Step 4: Save Connection**

1. Click **"Save Connection"** or **"Connect AWS"**
2. System will:
   - Test the AWS connection (AssumeRole)
   - Validate credentials
   - Save settings to database

3. **If successful:**
   - You'll see "AWS connection saved successfully!"
   - Redirected to dashboard
   - Can now see real cost data

---

## 🔍 Verify Connection

After connecting, verify:

1. **Check Dashboard:**
   - Go to Dashboard
   - Should show real cost data (not zeros)
   - Charts should populate

2. **Check Settings:**
   - Go to Settings
   - Should show "AWS Connected" status

3. **Test API:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:9000/api/dashboard
   ```
   Should return real cost data

---

## 🚨 Troubleshooting

### **Error: "Cannot AssumeRole"**
- **Check**: Role ARN is correct
- **Check**: External ID matches CloudFormation stack
- **Check**: IAM role trust policy allows your account

### **Error: "No CUR data found"**
- **Check**: CUR is enabled and generating reports
- **Check**: Wait 24-48 hours for first report
- **Check**: S3 bucket path is correct

### **Error: "Athena table not found"**
- **Check**: Database and table names are correct
- **Check**: CUR Athena integration is enabled
- **Check**: Table exists in Athena console

---

## ✅ After Connection

Once AWS is connected:

1. **Real cost data** will flow from CUR → Athena → Your app
2. **Anomaly detection** can train on real historical data
3. **CloudWatch metrics** can be collected
4. **All ML features** will use real data

---

## 🎯 Next Steps

After connecting AWS:

1. ✅ Wait for CUR data (24-48 hours if new)
2. ✅ Verify dashboard shows real costs
3. ✅ Implement anomaly detection model
4. ✅ Train on real historical data (90 days)
5. ✅ Start detecting anomalies in real-time

---

## 💡 Quick Reference

**API Endpoint:** `POST /api/tenants/connect`

**Required Fields:**
- `aws_role_arn`
- `external_id`
- `region`
- `athena_db`
- `athena_table`

**Optional Fields:**
- `cur_bucket`
- `cur_prefix`
- `athena_workgroup`
- `athena_results_bucket`
- `athena_results_prefix`



