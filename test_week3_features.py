#!/usr/bin/env python3
"""
Test Week 3: Advanced Analytics & Dashboard Features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def test_ml_ai_capabilities():
    """Test ML and AI capabilities"""
    print("✅ Testing ML and AI capabilities...")
    
    # Test anomaly detection
    print("\n🧠 Testing Anomaly Detection...")
    try:
        from sklearn.ensemble import IsolationForest
        
        # Generate sample data
        np.random.seed(42)
        normal_data = np.random.normal(100, 10, 50)
        anomaly_data = np.random.normal(200, 10, 5)
        data = np.concatenate([normal_data, anomaly_data])
        
        # Train anomaly detection model
        model = IsolationForest(contamination=0.1, random_state=42)
        predictions = model.fit_predict(data.reshape(-1, 1))
        anomalies = np.sum(predictions == -1)
        
        print(f"✅ Anomaly detection working: {anomalies} anomalies detected")
        print(f"✅ Model accuracy: {len(anomalies)/len(data)*100:.1f}% anomaly rate")
        
    except Exception as e:
        print(f"❌ Anomaly detection error: {e}")
    
    # Test cost forecasting
    print("\n🔮 Testing Cost Forecasting...")
    try:
        from sklearn.ensemble import RandomForestRegressor
        
        # Generate historical data
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        costs = 100 + np.cumsum(np.random.normal(2, 5, len(dates)))
        
        # Prepare features
        df = pd.DataFrame({'date': dates, 'cost': costs})
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['cost_lag_1'] = df['cost'].shift(1)
        df['cost_lag_7'] = df['cost'].shift(7)
        
        # Train model
        df_clean = df.dropna()
        X = df_clean[['day_of_week', 'month', 'cost_lag_1', 'cost_lag_7']]
        y = df_clean['cost']
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Make prediction
        last_features = X.iloc[-1].values.reshape(1, -1)
        prediction = model.predict(last_features)[0]
        
        print(f"✅ Cost forecasting working: ${prediction:.2f} predicted for next day")
        print(f"✅ Model trained on {len(df_clean)} data points")
        
    except Exception as e:
        print(f"❌ Cost forecasting error: {e}")
    
    # Test optimization recommendations
    print("\n⚡ Testing Optimization Recommendations...")
    try:
        # Simulate resource data
        resources = [
            {'name': 'WebServer-1', 'cpu': 25, 'memory': 40, 'cost': 200},
            {'name': 'DatabaseServer-1', 'cpu': 85, 'memory': 90, 'cost': 500},
            {'name': 'APIServer-1', 'cpu': 60, 'memory': 70, 'cost': 300},
            {'name': 'CacheServer-1', 'cpu': 15, 'memory': 20, 'cost': 150}
        ]
        
        recommendations = []
        for resource in resources:
            if resource['cpu'] < 30 and resource['memory'] < 40:
                savings = resource['cost'] * 0.3
                recommendations.append({
                    'resource': resource['name'],
                    'type': 'downsize',
                    'savings': savings
                })
            elif resource['cpu'] > 80 or resource['memory'] > 85:
                savings = resource['cost'] * 0.2
                recommendations.append({
                    'resource': resource['name'],
                    'type': 'upsize',
                    'savings': savings
                })
        
        total_savings = sum(rec['savings'] for rec in recommendations)
        print(f"✅ Optimization recommendations: {len(recommendations)} recommendations")
        print(f"✅ Total potential savings: ${total_savings:.2f}")
        
    except Exception as e:
        print(f"❌ Optimization recommendations error: {e}")

if __name__ == "__main__":
    test_ml_ai_capabilities()
    print("\n🎉 Week 3 testing completed!")
