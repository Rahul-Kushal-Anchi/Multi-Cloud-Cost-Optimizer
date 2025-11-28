# ML Cost Optimizer - Technical Architecture
**For Final Exam Presentation - December 13, 2025**

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AWS Customer Account                        │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │ Cost & Usage │    │   CloudWatch │    │  EC2 Instances  │   │
│  │ Report (CUR) │    │    Metrics   │    │                 │   │
│  └──────┬───────┘    └──────┬───────┘    └────────┬────────┘   │
│         │                   │                      │            │
│         ↓                   ↓                      ↓            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Amazon Athena                          │  │
│  │              (SQL queries on CUR data)                    │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└─────────────────────────────┼──────────────────────────────────┘
                              │
                              ↓ (Cross-account IAM Role)
┌─────────────────────────────────────────────────────────────────┐
│                   Our ML Cost Optimizer Platform                 │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI Backend                          │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐│ │
│  │  │   Anomaly    │  │ Right-Sizing │  │   Forecasting    ││ │
│  │  │   Detector   │  │    Model     │  │      Model       ││ │
│  │  │              │  │              │  │                  ││ │
│  │  │ Isolation    │  │  Instance    │  │    Prophet       ││ │
│  │  │   Forest     │  │  Analysis    │  │  Time Series     ││ │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘│ │
│  │         │                 │                    │          │ │
│  │         └─────────────────┼────────────────────┘          │ │
│  │                           │                               │ │
│  │                  ┌────────▼────────┐                      │ │
│  │                  │   PostgreSQL    │                      │ │
│  │                  │    Database     │                      │ │
│  │                  │  (Anomalies,    │                      │ │
│  │                  │ Recommendations,│                      │ │
│  │                  │   Forecasts)    │                      │ │
│  │                  └─────────────────┘                      │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    React Frontend                           │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐│ │
│  │  │  Anomalies   │  │ Right-Sizing │  │   Dashboard      ││ │
│  │  │     Page     │  │     Page     │  │  with Forecast   ││ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘│ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🤖 ML Models Detail

### 1. Anomaly Detection (Isolation Forest)

**Purpose:** Detect unusual cost patterns

**Input Features (19):**
- `daily_cost` - Daily spend
- `cost_change` - Day-over-day change
- `cost_change_pct` - Percentage change
- `rolling_mean_7d` - 7-day moving average
- `rolling_std_7d` - 7-day standard deviation
- `rolling_mean_30d` - 30-day moving average
- `z_score` - Statistical deviation
- `day_of_week` - Weekday patterns
- `is_weekend` - Weekend flag
- `cost_lag_1`, `cost_lag_7` - Lagged costs

**Training:**
```python
# Isolation Forest configuration
contamination=0.1  # Expect 10% anomalies
n_estimators=100   # 100 decision trees
random_state=42    # Reproducibility
```

**Output:**
- Anomaly score (lower = more anomalous)
- Classification: spike/drop/unusual_pattern
- Severity: critical/high/medium/low

**Data Source:** REAL AWS CUR (90 days minimum)

---

### 2. Right-Sizing (Instance Analysis)

**Purpose:** Recommend optimal EC2 instance types

**Input Metrics:**
- CPU utilization: mean, P95, P99
- Memory utilization: mean, P95, P99
- Network I/O patterns
- Current instance type & specs

**Algorithm:**
```python
1. Collect REAL CloudWatch metrics (14 days)
2. Calculate P95 utilization
3. Add 20% headroom for safety
4. Find smallest instance meeting requirements
5. Calculate savings using REAL AWS pricing
6. Assess risk level
```

**Output:**
- Current instance type
- Recommended instance type
- **Specific monthly savings** (e.g., $73.08)
- Savings percentage
- Risk level (low/medium/high)
- Confidence score (0-100)
- Reasoning text

**Data Source:** REAL EC2 instances + CloudWatch metrics

---

### 3. Cost Forecasting (Prophet)

**Purpose:** Predict future costs with confidence intervals

**Input:**
- Historical daily costs (90+ days)
- Date-cost pairs

**Model:**
```python
# Prophet configuration
weekly_seasonality=True    # Weekly patterns
yearly_seasonality=True    # Yearly if >365 days data
interval_width=0.95        # 95% confidence intervals
```

**Output:**
- Forecasted cost per day (30/60/90 days)
- Lower confidence bound
- Upper confidence bound
- Trend: increasing/decreasing/stable

**Data Source:** REAL AWS CUR historical data

---

## 📊 Data Flow

### Training Flow:
```
1. User clicks "Train Model"
   ↓
2. API fetches REAL data from AWS CUR via Athena
   ↓
3. Feature extraction (19 features for anomalies)
   ↓
4. Model training (Isolation Forest / Prophet)
   ↓
5. Model saved (pickle file + database metadata)
```

### Detection/Inference Flow:
```
1. User clicks "Detect" or "Analyze"
   ↓
2. Fetch recent REAL data from AWS
   ↓
3. Load trained model
   ↓
4. Run inference
   ↓
5. Save results to database
   ↓
6. Display in UI
```

---

## 🔒 Security & Data Privacy

### How We Access AWS Data:
- **Cross-Account IAM Role** with External ID
- Read-only permissions
- No data storage (queries on-demand)
- Customer data stays in their AWS account

### Data Processing:
- Queries run in real-time
- Results cached briefly (30 seconds)
- ML models trained per-tenant
- No cross-tenant data leakage

---

## 📈 Performance & Scalability

### Model Training Time:
- Anomaly Detection: ~5 seconds (90 days data)
- Right-Sizing: ~10 seconds (per tenant)
- Forecasting: ~8 seconds (90 days data)

### API Response Times:
- Dashboard: <500ms
- Anomaly Detection: <1s
- Right-Sizing: <2s (includes CloudWatch queries)
- Forecasting: <500ms (after training)

### Scalability:
- Multi-tenant architecture
- Models cached per-tenant
- Async CloudWatch collection
- Database-backed for persistence

---

## 🎯 Production Readiness

### What Makes It Production-Ready:

1. **REAL Data Only**
   - ✅ No mock/demo data
   - ✅ All queries on actual AWS CUR
   - ✅ CloudWatch metrics from real instances
   - ✅ AWS pricing data

2. **Error Handling**
   - ✅ Validates data availability (minimum days)
   - ✅ Fallback for missing memory metrics
   - ✅ Graceful degradation (Prophet → Linear if unavailable)

3. **Database Persistence**
   - ✅ Anomalies stored
   - ✅ Recommendations tracked
   - ✅ Forecasts saved
   - ✅ Model metadata versioned

4. **Testing**
   - ✅ Unit tests for services
   - ✅ End-to-end test scripts
   - ✅ Validated with real AWS account

---

## 🆚 Competitive Comparison

| Feature | AWS Cost Explorer | CloudHealth | **Our Platform** |
|---------|------------------|-------------|------------------|
| Anomaly Detection | Threshold-based | Rule-based | **ML-powered (Isolation Forest)** |
| Recommendations | Generic | Generic | **Specific: "Save $X/month"** |
| Forecasting | Basic | Simple | **Prophet with 95% CI** |
| Right-Sizing | Manual | Rule-based | **ML analysis of real usage** |
| Data Source | AWS only | Multi-cloud | **REAL AWS (expandable)** |

---

## 📚 Technical Stack Summary

### Backend:
- FastAPI 0.115.0
- SQLModel (ORM)
- boto3 (AWS SDK)
- scikit-learn 1.3.0+
- Prophet 1.1.4+

### Frontend:
- React 18+
- Recharts (visualizations)
- TailwindCSS
- React Query

### ML/Data:
- pandas, numpy
- Isolation Forest (anomaly detection)
- Prophet (forecasting)
- Real-time feature extraction

### Infrastructure:
- PostgreSQL database
- AWS ECS Fargate
- Docker containers
- GitHub Actions CI/CD

---

## 🎓 Key Takeaways for Presentation

1. **Emphasize REAL data** - say it multiple times
2. **Show specific savings** - "$73/month" not "optimize"
3. **ML vs competitors** - we learn patterns, they use thresholds
4. **Production-ready** - not a prototype, actual system
5. **Scalable architecture** - multi-tenant, database-backed

---

**Ready to impress on December 13! 🚀**

