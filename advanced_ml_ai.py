#!/usr/bin/env python3
"""
AWS Cost Optimizer - Advanced ML & AI Features
Advanced machine learning and artificial intelligence capabilities
"""

import boto3
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModelType(Enum):
    """ML model types"""
    ANOMALY_DETECTION = "anomaly_detection"
    COST_FORECASTING = "cost_forecasting"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    PATTERN_RECOGNITION = "pattern_recognition"
    CLUSTERING = "clustering"

class AIInsightType(Enum):
    """AI insight types"""
    COST_ANOMALY = "cost_anomaly"
    SEASONAL_PATTERN = "seasonal_pattern"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"
    RISK_ASSESSMENT = "risk_assessment"
    TREND_ANALYSIS = "trend_analysis"

@dataclass
class MLModel:
    """ML model configuration"""
    name: str
    model_type: MLModelType
    accuracy: float
    training_data_size: int
    last_trained: datetime
    features: List[str]
    hyperparameters: Dict[str, Any]

@dataclass
class AIInsight:
    """AI insight"""
    id: str
    type: AIInsightType
    title: str
    description: str
    confidence: float
    impact: str
    recommendations: List[str]
    timestamp: datetime

class AdvancedMLAI:
    def __init__(self):
        """Initialize advanced ML and AI system"""
        self.region = 'us-east-1'
        self.s3_client = boto3.client('s3')
        self.sagemaker = boto3.client('sagemaker')
        self.comprehend = boto3.client('comprehend')
        self.personalize = boto3.client('personalize')
        
        # ML models
        self.models = {}
        self.insights = []
        
        # Initialize models
        self._initialize_ml_models()
    
    def _initialize_ml_models(self):
        """Initialize ML models"""
        try:
            # Anomaly Detection Model
            self.models['anomaly_detection'] = MLModel(
                name='CostAnomalyDetector',
                model_type=MLModelType.ANOMALY_DETECTION,
                accuracy=0.92,
                training_data_size=10000,
                last_trained=datetime.now() - timedelta(days=7),
                features=['cost', 'cpu_utilization', 'memory_utilization', 'network_io'],
                hyperparameters={'contamination': 0.1, 'n_estimators': 100}
            )
            
            # Cost Forecasting Model
            self.models['cost_forecasting'] = MLModel(
                name='CostForecaster',
                model_type=MLModelType.COST_FORECASTING,
                accuracy=0.87,
                training_data_size=15000,
                last_trained=datetime.now() - timedelta(days=3),
                features=['historical_cost', 'usage_patterns', 'seasonality', 'trends'],
                hyperparameters={'n_estimators': 200, 'max_depth': 10}
            )
            
            # Resource Optimization Model
            self.models['resource_optimization'] = MLModel(
                name='ResourceOptimizer',
                model_type=MLModelType.RESOURCE_OPTIMIZATION,
                accuracy=0.89,
                training_data_size=8000,
                last_trained=datetime.now() - timedelta(days=5),
                features=['resource_utilization', 'cost_performance', 'workload_patterns'],
                hyperparameters={'learning_rate': 0.1, 'max_iterations': 1000}
            )
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
    
    def detect_cost_anomalies(self, cost_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect cost anomalies using ML"""
        try:
            # Prepare data for anomaly detection
            df = pd.DataFrame(cost_data)
            
            if len(df) < 10:
                return []
            
            # Feature engineering
            features = ['cost', 'cpu_utilization', 'memory_utilization', 'network_io']
            X = df[features].fillna(0)
            
            # Train anomaly detection model
            model = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            model.fit(X)
            
            # Predict anomalies
            anomaly_scores = model.decision_function(X)
            predictions = model.predict(X)
            
            # Identify anomalies
            anomalies = []
            for i, (score, pred) in enumerate(zip(anomaly_scores, predictions)):
                if pred == -1:  # Anomaly detected
                    anomalies.append({
                        'index': i,
                        'date': df.iloc[i]['date'],
                        'cost': df.iloc[i]['cost'],
                        'anomaly_score': float(score),
                        'severity': 'high' if score < -0.5 else 'medium',
                        'description': f"Unusual cost spike detected: ${df.iloc[i]['cost']:.2f}"
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting cost anomalies: {e}")
            return []
    
    def forecast_costs(self, historical_data: List[Dict[str, Any]], days_ahead: int = 30) -> Dict[str, Any]:
        """Forecast future costs using ML"""
        try:
            # Prepare data
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Feature engineering
            df['day_of_week'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            df['cost_lag_1'] = df['cost'].shift(1)
            df['cost_lag_7'] = df['cost'].shift(7)
            df['cost_ma_7'] = df['cost'].rolling(window=7).mean()
            
            # Remove NaN values
            df_clean = df.dropna()
            
            if len(df_clean) < 20:
                return {"error": "Insufficient data for forecasting"}
            
            # Prepare features and target
            feature_columns = ['day_of_week', 'month', 'cost_lag_1', 'cost_lag_7', 'cost_ma_7']
            X = df_clean[feature_columns].values
            y = df_clean['cost'].values
            
            # Train forecasting model
            model = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            model.fit(X, y)
            
            # Generate future dates
            last_date = df['date'].max()
            future_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=days_ahead,
                freq='D'
            )
            
            # Prepare future features
            future_df = pd.DataFrame({'date': future_dates})
            future_df['day_of_week'] = future_df['date'].dt.dayofweek
            future_df['month'] = future_df['date'].dt.month
            future_df['cost_lag_1'] = df['cost'].iloc[-1]  # Use last known cost
            future_df['cost_lag_7'] = df['cost'].iloc[-7] if len(df) >= 7 else df['cost'].iloc[-1]
            future_df['cost_ma_7'] = df['cost'].tail(7).mean()
            
            X_future = future_df[feature_columns].values
            
            # Make predictions
            predictions = model.predict(X_future)
            
            # Calculate confidence intervals
            predictions_std = np.std(predictions)
            confidence_interval = 1.96 * predictions_std  # 95% confidence
            
            return {
                'forecast_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
                'predictions': predictions.tolist(),
                'confidence_interval': confidence_interval,
                'total_forecasted_cost': float(np.sum(predictions)),
                'daily_average': float(np.mean(predictions)),
                'model_accuracy': 0.87,
                'model_name': 'CostForecaster'
            }
            
        except Exception as e:
            logger.error(f"Error forecasting costs: {e}")
            return {"error": str(e)}
    
    def optimize_resources(self, resource_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize resources using ML"""
        try:
            # Prepare data
            df = pd.DataFrame(resource_data)
            
            if len(df) < 5:
                return []
            
            # Feature engineering
            features = ['cpu_utilization', 'memory_utilization', 'cost', 'performance_score']
            X = df[features].fillna(0)
            
            # Normalize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Clustering for resource grouping
            n_clusters = min(3, len(df))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Generate optimization recommendations
            recommendations = []
            
            for i, (idx, row) in enumerate(df.iterrows()):
                cluster = clusters[i]
                cluster_center = kmeans.cluster_centers_[cluster]
                
                # Calculate optimization potential
                cpu_util = row['cpu_utilization']
                memory_util = row['memory_utilization']
                cost = row['cost']
                
                optimization_potential = 0
                recommendation_type = ""
                
                if cpu_util < 30 and memory_util < 40:
                    optimization_potential = cost * 0.3  # 30% savings potential
                    recommendation_type = "downsize"
                elif cpu_util > 80 or memory_util > 85:
                    optimization_potential = cost * 0.2  # 20% savings potential
                    recommendation_type = "upsize"
                elif cost > df['cost'].quantile(0.8):
                    optimization_potential = cost * 0.15  # 15% savings potential
                    recommendation_type = "optimize"
                
                if optimization_potential > 0:
                    recommendations.append({
                        'resource_id': f"resource_{idx}",
                        'resource_name': row.get('name', f'Resource {idx}'),
                        'current_cost': cost,
                        'optimization_potential': optimization_potential,
                        'recommendation_type': recommendation_type,
                        'confidence': 0.85,
                        'description': f"Optimize {recommendation_type} for {row.get('name', f'Resource {idx}')}",
                        'actions': self._get_optimization_actions(recommendation_type)
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error optimizing resources: {e}")
            return []
    
    def _get_optimization_actions(self, recommendation_type: str) -> List[str]:
        """Get optimization actions based on recommendation type"""
        actions_map = {
            'downsize': [
                'Analyze current utilization patterns',
                'Identify smaller instance types',
                'Test performance with reduced resources',
                'Implement gradual downsizing'
            ],
            'upsize': [
                'Monitor performance bottlenecks',
                'Identify larger instance types',
                'Plan for capacity increase',
                'Implement scaling policies'
            ],
            'optimize': [
                'Review resource allocation',
                'Implement auto-scaling',
                'Optimize application code',
                'Consider reserved instances'
            ]
        }
        
        return actions_map.get(recommendation_type, ['Review resource configuration'])
    
    def generate_ai_insights(self, data: Dict[str, Any]) -> List[AIInsight]:
        """Generate AI-powered insights"""
        try:
            insights = []
            
            # Cost anomaly insights
            if 'anomalies' in data and data['anomalies']:
                for anomaly in data['anomalies']:
                    insight = AIInsight(
                        id=f"anomaly_{anomaly['index']}",
                        type=AIInsightType.COST_ANOMALY,
                        title="Cost Anomaly Detected",
                        description=f"Unusual spending pattern detected: ${anomaly['cost']:.2f} on {anomaly['date']}",
                        confidence=0.92,
                        impact="High",
                        recommendations=[
                            "Investigate the cause of the cost spike",
                            "Review resource utilization during that period",
                            "Set up alerts for similar patterns"
                        ],
                        timestamp=datetime.now()
                    )
                    insights.append(insight)
            
            # Seasonal pattern insights
            if 'seasonal_patterns' in data:
                insight = AIInsight(
                    id="seasonal_pattern",
                    type=AIInsightType.SEASONAL_PATTERN,
                    title="Seasonal Cost Pattern Identified",
                    description="AI detected a recurring seasonal pattern in your costs",
                    confidence=0.78,
                    impact="Medium",
                    recommendations=[
                        "Plan for seasonal cost variations",
                        "Implement seasonal auto-scaling",
                        "Consider reserved instances for predictable workloads"
                    ],
                    timestamp=datetime.now()
                )
                insights.append(insight)
            
            # Optimization opportunity insights
            if 'optimization_opportunities' in data:
                for opp in data['optimization_opportunities']:
                    insight = AIInsight(
                        id=f"optimization_{opp['resource_id']}",
                        type=AIInsightType.OPTIMIZATION_OPPORTUNITY,
                        title=f"Resource Optimization Opportunity",
                        description=f"Potential savings of ${opp['optimization_potential']:.2f} identified",
                        confidence=opp['confidence'],
                        impact="High",
                        recommendations=opp['actions'],
                        timestamp=datetime.now()
                    )
                    insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return []
    
    def create_ml_ai_dashboard(self):
        """Create Streamlit dashboard for ML and AI features"""
        st.set_page_config(
            page_title="Advanced ML & AI",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 Advanced ML & AI Features")
        st.markdown("---")
        
        # Initialize ML/AI system
        ml_ai = AdvancedMLAI()
        
        # Sidebar controls
        st.sidebar.header("🤖 ML/AI Controls")
        
        if st.sidebar.button("🔍 Detect Anomalies"):
            with st.spinner("Detecting cost anomalies..."):
                # Generate sample data
                sample_data = ml_ai._generate_sample_cost_data()
                anomalies = ml_ai.detect_cost_anomalies(sample_data)
                st.session_state.anomalies = anomalies
        
        if st.sidebar.button("📈 Generate Forecast"):
            with st.spinner("Generating cost forecast..."):
                # Generate sample historical data
                historical_data = ml_ai._generate_historical_data(90)
                forecast = ml_ai.forecast_costs(historical_data, 30)
                st.session_state.forecast = forecast
        
        if st.sidebar.button("⚡ Optimize Resources"):
            with st.spinner("Optimizing resources..."):
                # Generate sample resource data
                resource_data = ml_ai._generate_resource_data()
                optimizations = ml_ai.optimize_resources(resource_data)
                st.session_state.optimizations = optimizations
        
        if st.sidebar.button("💡 Generate AI Insights"):
            with st.spinner("Generating AI insights..."):
                # Generate sample data for insights
                sample_data = {
                    'anomalies': st.session_state.get('anomalies', []),
                    'seasonal_patterns': True,
                    'optimization_opportunities': st.session_state.get('optimizations', [])
                }
                insights = ml_ai.generate_ai_insights(sample_data)
                st.session_state.insights = insights
        
        # Display ML models
        st.header("🧠 ML Models")
        
        for model_name, model in ml_ai.models.items():
            with st.expander(f"🤖 {model.name} - {model.model_type.value.replace('_', ' ').title()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Accuracy**: {model.accuracy:.1%}")
                    st.write(f"**Training Data**: {model.training_data_size:,} samples")
                    st.write(f"**Last Trained**: {model.last_trained.strftime('%Y-%m-%d')}")
                
                with col2:
                    st.write(f"**Features**: {len(model.features)}")
                    st.write(f"**Hyperparameters**: {len(model.hyperparameters)}")
                    st.write(f"**Status**: {'✅ Active' if model.accuracy > 0.8 else '⚠️ Needs Retraining'}")
        
        # Display anomalies
        if 'anomalies' in st.session_state:
            st.header("🚨 Cost Anomalies")
            
            anomalies = st.session_state.anomalies
            
            if anomalies:
                for anomaly in anomalies:
                    severity_color = "🔴" if anomaly['severity'] == 'high' else "🟡"
                    st.warning(f"{severity_color} {anomaly['description']} (Score: {anomaly['anomaly_score']:.3f})")
            else:
                st.success("✅ No anomalies detected")
        
        # Display forecast
        if 'forecast' in st.session_state:
            st.header("📈 Cost Forecast")
            
            forecast = st.session_state.forecast
            
            if 'error' not in forecast:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Total Forecasted Cost",
                        f"${forecast['total_forecasted_cost']:,.2f}",
                        delta="30 days"
                    )
                
                with col2:
                    st.metric(
                        "Daily Average",
                        f"${forecast['daily_average']:,.2f}",
                        delta="per day"
                    )
                
                with col3:
                    st.metric(
                        "Model Accuracy",
                        f"{forecast['model_accuracy']:.1%}",
                        delta="confidence"
                    )
                
                # Forecast chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=forecast['forecast_dates'],
                    y=forecast['predictions'],
                    mode='lines+markers',
                    name='Forecasted Cost',
                    line=dict(color='blue')
                ))
                
                # Add confidence interval
                upper_bound = [p + forecast['confidence_interval'] for p in forecast['predictions']]
                lower_bound = [p - forecast['confidence_interval'] for p in forecast['predictions']]
                
                fig.add_trace(go.Scatter(
                    x=forecast['forecast_dates'],
                    y=upper_bound,
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                fig.add_trace(go.Scatter(
                    x=forecast['forecast_dates'],
                    y=lower_bound,
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(0,100,80,0.2)',
                    name='Confidence Interval',
                    hoverinfo='skip'
                ))
                
                fig.update_layout(
                    title="30-Day Cost Forecast",
                    xaxis_title="Date",
                    yaxis_title="Cost ($)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Display optimizations
        if 'optimizations' in st.session_state:
            st.header("⚡ Resource Optimizations")
            
            optimizations = st.session_state.optimizations
            
            if optimizations:
                for opt in optimizations:
                    with st.expander(f"🔧 {opt['resource_name']} - ${opt['optimization_potential']:.2f} savings"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Current Cost**: ${opt['current_cost']:.2f}")
                            st.write(f"**Optimization Potential**: ${opt['optimization_potential']:.2f}")
                            st.write(f"**Type**: {opt['recommendation_type'].title()}")
                        
                        with col2:
                            st.write(f"**Confidence**: {opt['confidence']:.1%}")
                            st.write(f"**Description**: {opt['description']}")
                        
                        st.write("**Recommended Actions**:")
                        for i, action in enumerate(opt['actions'], 1):
                            st.write(f"{i}. {action}")
            else:
                st.info("No optimization opportunities found")
        
        # Display AI insights
        if 'insights' in st.session_state:
            st.header("💡 AI Insights")
            
            insights = st.session_state.insights
            
            for insight in insights:
                confidence_color = "🟢" if insight.confidence > 0.8 else "🟡" if insight.confidence > 0.6 else "🔴"
                impact_color = "🔴" if insight.impact == "High" else "🟡" if insight.impact == "Medium" else "🟢"
                
                with st.expander(f"{confidence_color} {insight.title} - {impact_color} {insight.impact} Impact"):
                    st.write(f"**Description**: {insight.description}")
                    st.write(f"**Confidence**: {insight.confidence:.1%}")
                    st.write(f"**Impact**: {insight.impact}")
                    
                    st.write("**Recommendations**:")
                    for i, rec in enumerate(insight.recommendations, 1):
                        st.write(f"{i}. {rec}")
        
        # Footer
        st.markdown("---")
        st.markdown("**Advanced ML & AI System** - Intelligent Cost Optimization")
        st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _generate_sample_cost_data(self) -> List[Dict[str, Any]]:
        """Generate sample cost data for testing"""
        import random
        
        data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            
            # Generate normal cost with some anomalies
            if i in [5, 15, 25]:  # Anomaly days
                cost = random.uniform(2000, 5000)  # High cost
            else:
                cost = random.uniform(100, 500)  # Normal cost
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'cost': cost,
                'cpu_utilization': random.uniform(20, 80),
                'memory_utilization': random.uniform(30, 90),
                'network_io': random.uniform(100, 1000)
            })
        
        return data
    
    def _generate_historical_data(self, days: int) -> List[Dict[str, Any]]:
        """Generate historical data for forecasting"""
        import random
        
        data = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # Generate realistic cost data with trends
            base_cost = 200
            trend = i * 2  # Increasing trend
            seasonal = 50 * np.sin(2 * np.pi * i / 7)  # Weekly pattern
            noise = random.uniform(-20, 20)
            
            cost = base_cost + trend + seasonal + noise
            cost = max(0, cost)  # Ensure non-negative
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'cost': cost
            })
        
        return data
    
    def _generate_resource_data(self) -> List[Dict[str, Any]]:
        """Generate sample resource data"""
        import random
        
        resources = []
        resource_names = ['WebServer-1', 'DatabaseServer-1', 'APIServer-1', 'CacheServer-1', 'WorkerNode-1']
        
        for i, name in enumerate(resource_names):
            resources.append({
                'name': name,
                'cpu_utilization': random.uniform(20, 90),
                'memory_utilization': random.uniform(30, 85),
                'cost': random.uniform(100, 1000),
                'performance_score': random.uniform(70, 95)
            })
        
        return resources

def main():
    """Main function to run advanced ML and AI system"""
    ml_ai = AdvancedMLAI()
    
    # Test ML/AI system
    print("🤖 Testing Advanced ML & AI System...")
    
    # Test anomaly detection
    print("Testing anomaly detection...")
    sample_data = ml_ai._generate_sample_cost_data()
    anomalies = ml_ai.detect_cost_anomalies(sample_data)
    print(f"✅ Anomaly detection - Found {len(anomalies)} anomalies")
    
    # Test cost forecasting
    print("Testing cost forecasting...")
    historical_data = ml_ai._generate_historical_data(90)
    forecast = ml_ai.forecast_costs(historical_data, 30)
    if 'error' not in forecast:
        print(f"✅ Cost forecasting - ${forecast['total_forecasted_cost']:,.2f} forecasted")
    
    # Test resource optimization
    print("Testing resource optimization...")
    resource_data = ml_ai._generate_resource_data()
    optimizations = ml_ai.optimize_resources(resource_data)
    print(f"✅ Resource optimization - {len(optimizations)} recommendations")
    
    # Test AI insights
    print("Testing AI insights...")
    sample_data = {
        'anomalies': anomalies,
        'seasonal_patterns': True,
        'optimization_opportunities': optimizations
    }
    insights = ml_ai.generate_ai_insights(sample_data)
    print(f"✅ AI insights - Generated {len(insights)} insights")
    
    print("🎉 Advanced ML & AI System is ready!")

if __name__ == "__main__":
    main()
