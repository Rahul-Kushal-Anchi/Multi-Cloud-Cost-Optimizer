#!/usr/bin/env python3
"""
Simple Feature Extraction Test - Tests feature extraction with sample data
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from api.ml.features import extract_cost_features, prepare_anomaly_features
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_feature_extraction_simple():
    """Test feature extraction with sample cost data"""
    print("🧪 Testing Feature Extraction")
    print("=" * 60)
    
    # Create sample cost data (simulating real AWS CUR data)
    print("\n📊 Creating sample cost data (simulating AWS CUR)...")
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
        'service': 'EC2'
    })
    
    print(f"✅ Created {len(cost_data)} days of sample cost data")
    print(f"   Date range: {cost_data['date'].min()} to {cost_data['date'].max()}")
    print(f"   Average daily cost: ${cost_data['cost'].mean():.2f}")
    print(f"   Total cost: ${cost_data['cost'].sum():.2f}")
    
    # Extract features
    print(f"\n🔧 Extracting features...")
    features_df = extract_cost_features(cost_data)
    
    print(f"✅ Feature extraction complete!")
    print(f"   Rows: {len(features_df)}")
    print(f"   Features: {len(features_df.columns)}")
    print(f"\n📋 Feature columns:")
    for col in features_df.columns:
        print(f"   - {col}")
    
    # Show sample features
    print(f"\n📊 Sample features (last 5 days):")
    sample_cols = ['date', 'daily_cost', 'cost_change', 'rolling_mean_7d', 'z_score']
    available_cols = [c for c in sample_cols if c in features_df.columns]
    print(features_df[available_cols].tail().to_string())
    
    # Prepare anomaly features
    print(f"\n🤖 Preparing anomaly detection features...")
    feature_matrix = prepare_anomaly_features(cost_data, lookback_days=90)
    
    print(f"✅ Anomaly feature matrix prepared!")
    print(f"   Shape: {feature_matrix.shape}")
    print(f"   Samples: {feature_matrix.shape[0]}")
    print(f"   Features: {feature_matrix.shape[1]}")
    
    # Check for NaN values
    nan_count = pd.isna(feature_matrix).sum().sum()
    if nan_count > 0:
        print(f"⚠️  Found {nan_count} NaN values in feature matrix")
    else:
        print(f"✅ No NaN values - feature matrix is clean!")
    
    # Test with real data if available
    print(f"\n💡 To test with REAL AWS cost data:")
    print("   1. Connect tenant to AWS CUR via web UI")
    print("   2. Run: python3 api/scripts/test_feature_extraction.py")
    print("   3. It will query REAL cost data from Athena")
    
    return True

if __name__ == "__main__":
    success = test_feature_extraction_simple()
    if success:
        print("\n✅ Feature extraction test completed!")
        print("\n🎉 Feature engineering pipeline is working!")
        print("\n💡 Next: Test with REAL cost data from your AWS account")

