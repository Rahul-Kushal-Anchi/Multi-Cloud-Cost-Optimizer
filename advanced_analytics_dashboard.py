#!/usr/bin/env python3
"""
AWS Cost Optimizer - Advanced Analytics Dashboard
Interactive dashboard with ML predictions and anomaly detection
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import boto3
import json
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAnalyticsDashboard:
    def __init__(self):
        """Initialize advanced analytics dashboard"""
        self.region = 'us-east-1'
        try:
            self.ce_client = boto3.client('ce')
            self.dynamodb = boto3.resource('dynamodb')
            self.s3_client = boto3.client('s3')
        except Exception as e:
            logger.error(f"Error initializing AWS clients: {e}")
            self.ce_client = None
            self.dynamodb = None
            self.s3_client = None
    
    def generate_sample_data(self, days=30):
        """Generate sample cost data for demonstration"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                            end=datetime.now() - timedelta(days=1), freq='D')
        
        # Generate realistic cost data with trends and seasonality
        base_cost = 100
        trend = np.linspace(0, 20, len(dates))
        seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)  # Weekly pattern
        noise = np.random.normal(0, 5, len(dates))
        
        costs = base_cost + trend + seasonal + noise
        costs = np.maximum(costs, 10)  # Ensure positive costs
        
        return pd.DataFrame({
            'date': dates,
            'cost': costs,
            'services': np.random.randint(3, 8, len(dates)),
            'regions': np.random.randint(2, 5, len(dates))
        })
    
    def detect_anomalies(self, df):
        """Detect cost anomalies using ML"""
        try:
            if len(df) < 10:
                return df.copy()
            
            # Prepare features
            features = ['cost']
            X = df[features].values
            
            # Train anomaly detection model
            model = IsolationForest(contamination=0.1, random_state=42)
            predictions = model.fit_predict(X)
            
            # Add anomaly flag
            df_result = df.copy()
            df_result['is_anomaly'] = predictions == -1
            df_result['anomaly_score'] = model.decision_function(X)
            
            return df_result
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            df_result = df.copy()
            df_result['is_anomaly'] = False
            df_result['anomaly_score'] = 0
            return df_result
    
    def generate_forecast(self, df, days_ahead=7):
        """Generate cost forecast using ML"""
        try:
            if len(df) < 10:
                return None
            
            # Prepare features
            df_features = df.copy()
            df_features['day_of_week'] = df_features['date'].dt.dayofweek
            df_features['month'] = df_features['date'].dt.month
            df_features['cost_lag_1'] = df_features['cost'].shift(1)
            df_features['cost_lag_7'] = df_features['cost'].shift(7)
            df_features['cost_ma_7'] = df_features['cost'].rolling(window=7).mean()
            
            # Remove NaN values
            df_clean = df_features.dropna()
            
            if len(df_clean) < 5:
                return None
            
            # Prepare training data
            feature_columns = ['day_of_week', 'month', 'cost_lag_1', 'cost_lag_7', 'cost_ma_7']
            X = df_clean[feature_columns].values
            y = df_clean['cost'].values
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Generate forecast
            forecast_dates = pd.date_range(start=df['date'].max() + timedelta(days=1), 
                                         periods=days_ahead, freq='D')
            
            forecasts = []
            for i, date in enumerate(forecast_dates):
                # Use last known values for features
                last_row = df_clean.iloc[-1]
                features = [
                    date.dayofweek,
                    date.month,
                    last_row['cost'],
                    df_clean['cost'].iloc[-7] if len(df_clean) >= 7 else last_row['cost'],
                    df_clean['cost'].tail(7).mean()
                ]
                
                prediction = model.predict([features])[0]
                forecasts.append({
                    'date': date,
                    'predicted_cost': max(0, prediction),
                    'confidence': 0.85
                })
            
            return pd.DataFrame(forecasts)
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return None
    
    def get_optimization_recommendations(self):
        """Get cost optimization recommendations"""
        recommendations = [
            {
                'type': 'rightsizing',
                'title': 'Downsize Underutilized EC2 Instances',
                'description': '3 EC2 instances are running at less than 30% CPU utilization',
                'potential_savings': 450.00,
                'priority': 'high',
                'confidence': 0.92
            },
            {
                'type': 'reserved_instances',
                'title': 'Purchase Reserved Instances',
                'description': 'Consistent workload patterns detected for 2 instance types',
                'potential_savings': 800.00,
                'priority': 'medium',
                'confidence': 0.78
            },
            {
                'type': 'storage_optimization',
                'title': 'Optimize S3 Storage Classes',
                'description': 'Move infrequently accessed data to IA storage class',
                'potential_savings': 200.00,
                'priority': 'low',
                'confidence': 0.85
            },
            {
                'type': 'database_optimization',
                'title': 'Optimize RDS Instance Types',
                'description': 'Database instances can be downsized based on usage patterns',
                'potential_savings': 350.00,
                'priority': 'medium',
                'confidence': 0.80
            }
        ]
        
        return recommendations

def main():
    """Main Streamlit dashboard"""
    st.set_page_config(
        page_title="Advanced Analytics Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Advanced Analytics Dashboard")
    st.markdown("---")
    
    # Initialize dashboard
    dashboard = AdvancedAnalyticsDashboard()
    
    # Sidebar controls
    st.sidebar.header("📊 Dashboard Controls")
    
    days = st.sidebar.slider("Days to analyze", 7, 90, 30)
    show_forecast = st.sidebar.checkbox("Show Forecast", value=True)
    show_anomalies = st.sidebar.checkbox("Show Anomalies", value=True)
    
    # Generate sample data
    with st.spinner("Loading cost data..."):
        df = dashboard.generate_sample_data(days)
    
    # Detect anomalies
    if show_anomalies:
        with st.spinner("Detecting anomalies..."):
            df = dashboard.detect_anomalies(df)
    
    # Generate forecast
    forecast_df = None
    if show_forecast:
        with st.spinner("Generating forecast..."):
            forecast_df = dashboard.generate_forecast(df, 7)
    
    # Key metrics
    st.header("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cost = df['cost'].sum()
        st.metric("Total Cost", f"${total_cost:,.2f}", delta=f"Last {days} days")
    
    with col2:
        avg_daily = df['cost'].mean()
        st.metric("Daily Average", f"${avg_daily:.2f}", delta="per day")
    
    with col3:
        max_cost = df['cost'].max()
        st.metric("Peak Cost", f"${max_cost:.2f}", delta="highest day")
    
    with col4:
        anomalies = df['is_anomaly'].sum() if 'is_anomaly' in df.columns else 0
        st.metric("Anomalies", f"{anomalies}", delta="detected")
    
    # Cost trend chart
    st.header("📈 Cost Trend Analysis")
    
    fig = go.Figure()
    
    # Add cost line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['cost'],
        mode='lines+markers',
        name='Daily Cost',
        line=dict(color='blue', width=2)
    ))
    
    # Add anomaly points
    if show_anomalies and 'is_anomaly' in df.columns:
        anomalies_df = df[df['is_anomaly']]
        if not anomalies_df.empty:
            fig.add_trace(go.Scatter(
                x=anomalies_df['date'],
                y=anomalies_df['cost'],
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=10, symbol='x')
            ))
    
    # Add forecast
    if show_forecast and forecast_df is not None:
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['predicted_cost'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='green', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title="Cost Trend with Anomaly Detection and Forecasting",
        xaxis_title="Date",
        yaxis_title="Cost ($)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Service breakdown
    st.header("🔧 Service Breakdown")
    
    # Generate sample service data
    services = ['EC2', 'RDS', 'S3', 'Lambda', 'CloudWatch', 'ELB', 'EBS', 'Other']
    service_costs = np.random.dirichlet(np.ones(len(services))) * total_cost
    
    service_df = pd.DataFrame({
        'Service': services,
        'Cost': service_costs,
        'Percentage': service_costs / total_cost * 100
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(service_df, values='Cost', names='Service', 
                        title="Cost Distribution by Service")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(service_df, x='Service', y='Cost', 
                        title="Cost by Service")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Optimization recommendations
    st.header("💡 Optimization Recommendations")
    
    recommendations = dashboard.get_optimization_recommendations()
    total_savings = sum(rec['potential_savings'] for rec in recommendations)
    
    st.metric("Total Potential Savings", f"${total_savings:,.2f}", delta="monthly")
    
    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"🎯 {rec['title']} - {rec['priority'].upper()} Priority"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Type**: {rec['type'].title()}")
                st.write(f"**Description**: {rec['description']}")
                st.write(f"**Confidence**: {rec['confidence']:.1%}")
            
            with col2:
                st.metric("Potential Savings", f"${rec['potential_savings']:,.2f}")
                st.write(f"**Priority**: {rec['priority'].title()}")
    
    # Forecast details
    if show_forecast and forecast_df is not None:
        st.header("🔮 Cost Forecast")
        
        forecast_total = forecast_df['predicted_cost'].sum()
        st.metric("7-Day Forecast", f"${forecast_total:,.2f}", delta="predicted")
        
        fig_forecast = px.line(forecast_df, x='date', y='predicted_cost',
                              title="7-Day Cost Forecast",
                              labels={'predicted_cost': 'Predicted Cost ($)', 'date': 'Date'})
        st.plotly_chart(fig_forecast, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**Advanced Analytics Dashboard** - ML-Powered Cost Optimization")
    st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
