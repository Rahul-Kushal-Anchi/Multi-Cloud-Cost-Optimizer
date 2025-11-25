# ML Module - Cost Optimization

This module contains ML models and utilities for cost optimization features.

## Structure

- `features.py` - Feature engineering pipeline
- `models.py` - Database schema for ML models, anomalies, recommendations
- `anomaly_detector.py` - Anomaly detection model (to be implemented)
- `right_sizing.py` - Right-sizing recommendation model (to be implemented)
- `forecasting.py` - Cost forecasting model (to be implemented)

## Features

### 1. Feature Engineering (`features.py`)
- Extract cost features for anomaly detection
- Extract utilization features for right-sizing
- Prepare feature matrices for ML models

### 2. Database Schema (`models.py`)
- `MLModel` - Track trained models
- `Anomaly` - Store anomaly detection results
- `Recommendation` - Store right-sizing recommendations
- `Forecast` - Store cost forecasts
- `InstanceMetrics` - Store CloudWatch metrics

### 3. CloudWatch Integration (`api/secure/aws/cloudwatch.py`)
- Collect REAL EC2 instance metrics
- Get CPU, memory, network metrics
- Store metrics in database

## Usage

```python
from api.ml.features import extract_cost_features, prepare_anomaly_features
from api.secure.aws.cloudwatch import collect_all_instance_metrics

# Extract features from cost data
features = extract_cost_features(cost_data)

# Collect CloudWatch metrics
metrics = collect_all_instance_metrics(session, lookback_days=7)
```

## Requirements

- scikit-learn >= 1.3.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- prophet >= 1.1.4 (for forecasting)

## Next Steps

1. Implement anomaly detection model (`anomaly_detector.py`)
2. Implement right-sizing model (`right_sizing.py`)
3. Implement forecasting model (`forecasting.py`)
4. Create API endpoints for ML features
5. Build UI components for ML insights

