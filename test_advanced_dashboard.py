#!/usr/bin/env python3
"""
Test Advanced Analytics Dashboard
"""

import sys
sys.path.append('.')
from advanced_analytics_dashboard import AdvancedAnalyticsDashboard
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_advanced_dashboard():
    """Test the advanced analytics dashboard"""
    print("✅ Testing Advanced Analytics Dashboard...")
    
    # Initialize dashboard
    dashboard = AdvancedAnalyticsDashboard()
    
    # Test data generation
    print("\n📊 Testing data generation...")
    df = dashboard.generate_sample_data(30)
    print(f"✅ Generated {len(df)} days of sample data")
    print(f"✅ Cost range: ${df['cost'].min():.2f} - ${df['cost'].max():.2f}")
    
    # Test anomaly detection
    print("\n🧠 Testing anomaly detection...")
    df_with_anomalies = dashboard.detect_anomalies(df)
    anomalies = df_with_anomalies['is_anomaly'].sum()
    print(f"✅ Anomaly detection working: {anomalies} anomalies detected")
    
    # Test forecasting
    print("\n🔮 Testing cost forecasting...")
    forecast = dashboard.generate_forecast(df, 7)
    if forecast is not None:
        print(f"✅ Forecasting working: ${forecast['predicted_cost'].sum():.2f} predicted for 7 days")
    else:
        print("⚠️ Forecasting needs more data")
    
    # Test recommendations
    print("\n💡 Testing optimization recommendations...")
    recommendations = dashboard.get_optimization_recommendations()
    total_savings = sum(rec['potential_savings'] for rec in recommendations)
    print(f"✅ Recommendations working: {len(recommendations)} recommendations, ${total_savings:.2f} total savings")
    
    print("\n🎉 Advanced Analytics Dashboard is working!")

if __name__ == "__main__":
    test_advanced_dashboard()
