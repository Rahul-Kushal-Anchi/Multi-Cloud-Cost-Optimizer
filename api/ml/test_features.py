#!/usr/bin/env python3
"""
Test feature extraction functions
Run this to verify feature engineering works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from api.ml.features import extract_cost_features, prepare_anomaly_features

def test_cost_features():
    """Test cost feature extraction"""
    print("🧪 Testing cost feature extraction...")
    
    # Create sample cost data (simulating real AWS CUR data)
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    np.random.seed(42)
    
    # Simulate realistic cost patterns
    base_cost = 100
    trend = np.linspace(0, 20, len(dates))
    seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 30)
    noise = np.random.normal(0, 5, len(dates))
    costs = base_cost + trend + seasonal + noise
    
    cost_data = pd.DataFrame({
        'date': dates,
        'cost': costs,
        'service': 'EC2'  # Example service
    })
    
    # Extract features
    features_df = extract_cost_features(cost_data)
    
    print(f"✅ Extracted {len(features_df)} rows with {len(features_df.columns)} features")
    print(f"   Features: {list(features_df.columns)}")
    
    # Check for required features
    required_features = ['daily_cost', 'cost_change', 'rolling_mean_7d', 'z_score']
    missing = [f for f in required_features if f not in features_df.columns]
    
    if missing:
        print(f"❌ Missing features: {missing}")
        return False
    else:
        print("✅ All required features present")
    
    # Test anomaly feature preparation
    feature_matrix = prepare_anomaly_features(cost_data, lookback_days=90)
    print(f"✅ Prepared anomaly feature matrix: {feature_matrix.shape}")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing ML Feature Engineering")
    print("=" * 60)
    
    if test_cost_features():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

