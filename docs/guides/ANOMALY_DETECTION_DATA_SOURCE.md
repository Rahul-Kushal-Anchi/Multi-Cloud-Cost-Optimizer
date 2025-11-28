# Anomaly Detection Data Source

## 📊 Where Does the Data Come From?

For anomaly detection, we need **REAL cost data** from your AWS account. Here's how it works:

---

## 🔄 Data Flow

```
AWS Account
    ↓
Cost and Usage Report (CUR) → S3 Bucket
    ↓
Athena Database (queries CUR data)
    ↓
Our Application (queries Athena)
    ↓
ML Model (trains on historical data)
    ↓
Anomaly Detection (detects anomalies in real-time)
```

---

## 📍 Data Sources

### 1. **AWS Cost and Usage Report (CUR)**
- **What it is**: Detailed billing data from AWS
- **Where**: Stored in S3 bucket (configured in AWS)
- **Format**: Parquet files (daily/monthly)
- **Contains**: 
  - Daily costs per service
  - Resource-level costs
  - Usage metrics
  - Timestamps

### 2. **Athena Database**
- **What it is**: AWS service that queries CUR data from S3
- **How we use it**: SQL queries to get cost data
- **Current setup**: Already configured in your tenant settings
  - `athena_db`: Database name
  - `athena_table`: Table name (points to CUR)
  - `athena_workgroup`: Workgroup for queries

### 3. **Our Application**
- **Current code**: `api/secure/aws/athena_costs.py`
- **Function**: `fetch_tenant_cost_data()` - already queries Athena
- **What we'll use**: Same mechanism for anomaly detection

---

## 🎯 For Anomaly Detection

### **Training Data (90 days historical)**
```python
# Query Athena for last 90 days of cost data
query = """
SELECT
  date(line_item_usage_start_date) AS date,
  SUM(CAST(line_item_unblended_cost AS double)) AS cost
FROM {athena_table}
WHERE line_item_usage_start_date >= date_add('day', -90, current_timestamp)
  AND "$path" LIKE '%.parquet'
GROUP BY date(line_item_usage_start_date)
ORDER BY date ASC
"""
```

**This gives us:**
- 90 days of daily cost data
- Real historical patterns
- Baseline for anomaly detection

### **Real-Time Detection Data**
```python
# Query Athena for recent cost data (last 7 days)
query = """
SELECT
  date(line_item_usage_start_date) AS date,
  SUM(CAST(line_item_unblended_cost AS double)) AS cost
FROM {athena_table}
WHERE line_item_usage_start_date >= date_add('day', -7, current_timestamp)
  AND "$path" LIKE '%.parquet'
GROUP BY date(line_item_usage_start_date)
ORDER BY date ASC
"""
```

**This gives us:**
- Recent cost data to check for anomalies
- Compare against trained model
- Detect spikes, drops, unusual patterns

---

## ✅ Prerequisites

To get real data, you need:

1. **AWS Account Connected**
   - Tenant configured with AWS Role ARN
   - External ID set
   - Region configured

2. **CUR Setup**
   - Cost and Usage Report enabled in AWS
   - CUR data being written to S3
   - Athena database/table configured

3. **Athena Configuration**
   - Database name (`athena_db`)
   - Table name (`athena_table`)
   - Workgroup (`athena_workgroup`)

---

## 🔧 How We'll Use It

### **Step 1: Train Model**
```python
# Get 90 days of historical cost data
cost_data = fetch_cost_data_from_athena(tenant, days=90)

# Extract features
features = extract_cost_features(cost_data)

# Train Isolation Forest model
model = train_anomaly_model(features)

# Save model
save_model(model, tenant_id)
```

### **Step 2: Detect Anomalies**
```python
# Get recent cost data (last 7 days)
recent_data = fetch_cost_data_from_athena(tenant, days=7)

# Extract features
features = extract_cost_features(recent_data)

# Detect anomalies
anomalies = model.detect_anomalies(features)

# Save to database
save_anomalies(anomalies, tenant_id)
```

---

## 📋 Current Status

✅ **Already Working:**
- Athena query functions (`api/secure/aws/athena_costs.py`)
- Cost data fetching (`fetch_tenant_cost_data()`)
- Feature extraction (`api/ml/features.py`)

⏳ **To Implement:**
- Anomaly detection model training
- Real-time anomaly detection
- Anomaly storage and API

---

## 💡 Summary

**Real data comes from:**
1. AWS Cost and Usage Report (CUR) → S3
2. Athena queries CUR data → Returns cost data
3. Our app queries Athena → Gets daily costs
4. ML model uses this data → Detects anomalies

**No mock data needed** - everything uses real AWS cost data!



## 📊 Where Does the Data Come From?

For anomaly detection, we need **REAL cost data** from your AWS account. Here's how it works:

---

## 🔄 Data Flow

```
AWS Account
    ↓
Cost and Usage Report (CUR) → S3 Bucket
    ↓
Athena Database (queries CUR data)
    ↓
Our Application (queries Athena)
    ↓
ML Model (trains on historical data)
    ↓
Anomaly Detection (detects anomalies in real-time)
```

---

## 📍 Data Sources

### 1. **AWS Cost and Usage Report (CUR)**
- **What it is**: Detailed billing data from AWS
- **Where**: Stored in S3 bucket (configured in AWS)
- **Format**: Parquet files (daily/monthly)
- **Contains**: 
  - Daily costs per service
  - Resource-level costs
  - Usage metrics
  - Timestamps

### 2. **Athena Database**
- **What it is**: AWS service that queries CUR data from S3
- **How we use it**: SQL queries to get cost data
- **Current setup**: Already configured in your tenant settings
  - `athena_db`: Database name
  - `athena_table`: Table name (points to CUR)
  - `athena_workgroup`: Workgroup for queries

### 3. **Our Application**
- **Current code**: `api/secure/aws/athena_costs.py`
- **Function**: `fetch_tenant_cost_data()` - already queries Athena
- **What we'll use**: Same mechanism for anomaly detection

---

## 🎯 For Anomaly Detection

### **Training Data (90 days historical)**
```python
# Query Athena for last 90 days of cost data
query = """
SELECT
  date(line_item_usage_start_date) AS date,
  SUM(CAST(line_item_unblended_cost AS double)) AS cost
FROM {athena_table}
WHERE line_item_usage_start_date >= date_add('day', -90, current_timestamp)
  AND "$path" LIKE '%.parquet'
GROUP BY date(line_item_usage_start_date)
ORDER BY date ASC
"""
```

**This gives us:**
- 90 days of daily cost data
- Real historical patterns
- Baseline for anomaly detection

### **Real-Time Detection Data**
```python
# Query Athena for recent cost data (last 7 days)
query = """
SELECT
  date(line_item_usage_start_date) AS date,
  SUM(CAST(line_item_unblended_cost AS double)) AS cost
FROM {athena_table}
WHERE line_item_usage_start_date >= date_add('day', -7, current_timestamp)
  AND "$path" LIKE '%.parquet'
GROUP BY date(line_item_usage_start_date)
ORDER BY date ASC
"""
```

**This gives us:**
- Recent cost data to check for anomalies
- Compare against trained model
- Detect spikes, drops, unusual patterns

---

## ✅ Prerequisites

To get real data, you need:

1. **AWS Account Connected**
   - Tenant configured with AWS Role ARN
   - External ID set
   - Region configured

2. **CUR Setup**
   - Cost and Usage Report enabled in AWS
   - CUR data being written to S3
   - Athena database/table configured

3. **Athena Configuration**
   - Database name (`athena_db`)
   - Table name (`athena_table`)
   - Workgroup (`athena_workgroup`)

---

## 🔧 How We'll Use It

### **Step 1: Train Model**
```python
# Get 90 days of historical cost data
cost_data = fetch_cost_data_from_athena(tenant, days=90)

# Extract features
features = extract_cost_features(cost_data)

# Train Isolation Forest model
model = train_anomaly_model(features)

# Save model
save_model(model, tenant_id)
```

### **Step 2: Detect Anomalies**
```python
# Get recent cost data (last 7 days)
recent_data = fetch_cost_data_from_athena(tenant, days=7)

# Extract features
features = extract_cost_features(recent_data)

# Detect anomalies
anomalies = model.detect_anomalies(features)

# Save to database
save_anomalies(anomalies, tenant_id)
```

---

## 📋 Current Status

✅ **Already Working:**
- Athena query functions (`api/secure/aws/athena_costs.py`)
- Cost data fetching (`fetch_tenant_cost_data()`)
- Feature extraction (`api/ml/features.py`)

⏳ **To Implement:**
- Anomaly detection model training
- Real-time anomaly detection
- Anomaly storage and API

---

## 💡 Summary

**Real data comes from:**
1. AWS Cost and Usage Report (CUR) → S3
2. Athena queries CUR data → Returns cost data
3. Our app queries Athena → Gets daily costs
4. ML model uses this data → Detects anomalies

**No mock data needed** - everything uses real AWS cost data!



