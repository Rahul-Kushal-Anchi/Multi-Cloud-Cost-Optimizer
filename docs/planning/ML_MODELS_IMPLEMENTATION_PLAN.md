# ML Models Implementation Plan
## Detailed Technical Specification

---

## 🎯 **MODEL 1: Anomaly Detection**

### **Architecture**

```python
# api/ml/anomaly_detector.py

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta

class CostAnomalyDetector:
    """
    ML-based anomaly detection for cost spikes and unusual patterns.
    Uses Isolation Forest + Statistical methods for hybrid detection.
    """
    
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.baseline_mean = None
        self.baseline_std = None
        
    def extract_features(self, cost_data: pd.DataFrame) -> np.ndarray:
        """
        Extract features for anomaly detection:
        - Daily cost
        - Cost change (day-over-day)
        - Cost change percentage
        - Rolling average (7-day)
        - Rolling std dev (7-day)
        - Z-score
        - Service-level costs
        """
        features = []
        
        # Daily cost
        features.append(cost_data['cost'].values)
        
        # Day-over-day change
        cost_change = cost_data['cost'].diff().fillna(0)
        features.append(cost_change.values)
        
        # Percentage change
        pct_change = cost_data['cost'].pct_change().fillna(0) * 100
        features.append(pct_change.values)
        
        # Rolling statistics
        rolling_mean = cost_data['cost'].rolling(window=7).mean().fillna(cost_data['cost'].mean())
        rolling_std = cost_data['cost'].rolling(window=7).std().fillna(cost_data['cost'].std())
        features.append(rolling_mean.values)
        features.append(rolling_std.values)
        
        # Z-score
        z_score = (cost_data['cost'] - rolling_mean) / (rolling_std + 1e-6)
        features.append(z_score.values)
        
        # Service-level features (top 5 services)
        for service in cost_data['service'].unique()[:5]:
            service_costs = cost_data[cost_data['service'] == service]['cost'].values
            if len(service_costs) > 0:
                features.append(service_costs)
        
        # Stack features
        feature_matrix = np.column_stack(features)
        return feature_matrix
    
    def train(self, historical_data: pd.DataFrame):
        """Train the anomaly detection model on historical data."""
        features = self.extract_features(historical_data)
        features_scaled = self.scaler.fit_transform(features)
        
        # Train Isolation Forest
        self.isolation_forest.fit(features_scaled)
        
        # Calculate baseline statistics
        self.baseline_mean = historical_data['cost'].mean()
        self.baseline_std = historical_data['cost'].std()
        
    def detect_anomalies(self, current_data: pd.DataFrame) -> list:
        """
        Detect anomalies in current cost data.
        Returns list of anomaly objects.
        """
        features = self.extract_features(current_data)
        features_scaled = self.scaler.transform(features)
        
        # Predict anomalies
        predictions = self.isolation_forest.predict(features_scaled)
        anomaly_scores = self.isolation_forest.score_samples(features_scaled)
        
        anomalies = []
        for idx, (is_anomaly, score) in enumerate(zip(predictions, anomaly_scores)):
            if is_anomaly == -1:  # Anomaly detected
                anomaly = {
                    'date': current_data.iloc[idx]['date'],
                    'cost': current_data.iloc[idx]['cost'],
                    'anomaly_score': float(score),
                    'severity': self._calculate_severity(score, current_data.iloc[idx]['cost']),
                    'type': self._classify_anomaly_type(current_data.iloc[idx], current_data),
                    'affected_services': self._get_affected_services(current_data.iloc[idx]),
                    'estimated_impact': self._estimate_impact(current_data.iloc[idx])
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_severity(self, score: float, cost: float) -> str:
        """Calculate anomaly severity (low/medium/high/critical)."""
        z_score = abs((cost - self.baseline_mean) / (self.baseline_std + 1e-6))
        
        if z_score > 3 or score < -0.5:
            return 'critical'
        elif z_score > 2 or score < -0.3:
            return 'high'
        elif z_score > 1.5 or score < -0.1:
            return 'medium'
        else:
            return 'low'
    
    def _classify_anomaly_type(self, data_point: pd.Series, full_data: pd.DataFrame) -> str:
        """Classify anomaly type: spike, drop, pattern_change."""
        # Compare with previous day
        prev_cost = full_data[full_data['date'] < data_point['date']]['cost'].iloc[-1] if len(full_data[full_data['date'] < data_point['date']]) > 0 else data_point['cost']
        
        cost_change = ((data_point['cost'] - prev_cost) / prev_cost) * 100
        
        if cost_change > 50:
            return 'spike'
        elif cost_change < -50:
            return 'drop'
        else:
            return 'pattern_change'
    
    def _get_affected_services(self, data_point: pd.Series) -> list:
        """Get list of services contributing to anomaly."""
        # This would query service-level costs for the anomaly date
        # For now, return mock data
        return ['EC2', 'S3', 'RDS']
    
    def _estimate_impact(self, data_point: pd.Series) -> float:
        """Estimate financial impact of anomaly."""
        excess_cost = max(0, data_point['cost'] - self.baseline_mean)
        return float(excess_cost)
```

### **API Endpoint**

```python
# api/routers/ml_anomalies.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from api.secure.deps import get_session
from api.ml.anomaly_detector import CostAnomalyDetector
from api.secure.aws.athena_costs import fetch_cost_data_for_ml
import pandas as pd

router = APIRouter(prefix="/api/ml", tags=["ML"])

@router.get("/anomalies")
async def get_anomalies(
    days: int = 30,
    session: Session = Depends(get_session),
    authorization: str = Header(...)
):
    """
    Get cost anomalies detected by ML model.
    """
    # Fetch cost data
    cost_data = await fetch_cost_data_for_ml(days)
    
    # Initialize detector
    detector = CostAnomalyDetector()
    
    # Train on historical data (last 90 days)
    historical_data = await fetch_cost_data_for_ml(90)
    detector.train(historical_data)
    
    # Detect anomalies
    anomalies = detector.detect_anomalies(cost_data)
    
    return {
        "anomalies": anomalies,
        "total_anomalies": len(anomalies),
        "critical_count": len([a for a in anomalies if a['severity'] == 'critical']),
        "estimated_impact": sum([a['estimated_impact'] for a in anomalies])
    }
```

---

## 🎯 **MODEL 2: Right-Sizing Recommendations**

### **Architecture**

```python
# api/ml/right_sizing.py

import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import pandas as pd
from typing import Dict, List

class RightSizingRecommender:
    """
    ML model to recommend optimal instance sizes based on actual usage.
    """
    
    # AWS EC2 instance specs (example)
    INSTANCE_SPECS = {
        'm5.large': {'vCPU': 2, 'memory_gb': 8, 'price_per_hour': 0.096},
        'm5.xlarge': {'vCPU': 4, 'memory_gb': 16, 'price_per_hour': 0.192},
        'm5.2xlarge': {'vCPU': 8, 'memory_gb': 32, 'price_per_hour': 0.384},
        'm5.4xlarge': {'vCPU': 16, 'memory_gb': 64, 'price_per_hour': 0.768},
        'c5.large': {'vCPU': 2, 'memory_gb': 4, 'price_per_hour': 0.085},
        'c5.xlarge': {'vCPU': 4, 'memory_gb': 8, 'price_per_hour': 0.17},
        'r5.large': {'vCPU': 2, 'memory_gb': 16, 'price_per_hour': 0.126},
        'r5.xlarge': {'vCPU': 4, 'memory_gb': 32, 'price_per_hour': 0.252},
    }
    
    def __init__(self):
        self.cpu_model = LinearRegression()
        self.memory_model = LinearRegression()
        self.cluster_model = KMeans(n_clusters=5, random_state=42)
        
    def extract_features(self, cloudwatch_data: pd.DataFrame) -> Dict:
        """
        Extract features from CloudWatch metrics:
        - CPU utilization (avg, p95, p99)
        - Memory utilization (avg, p95, p99)
        - Network I/O
        - Disk I/O
        """
        features = {
            'cpu_avg': cloudwatch_data['CPUUtilization'].mean(),
            'cpu_p95': cloudwatch_data['CPUUtilization'].quantile(0.95),
            'cpu_p99': cloudwatch_data['CPUUtilization'].quantile(0.99),
            'memory_avg': cloudwatch_data['MemoryUtilization'].mean(),
            'memory_p95': cloudwatch_data['MemoryUtilization'].quantile(0.95),
            'memory_p99': cloudwatch_data['MemoryUtilization'].quantile(0.99),
            'network_in': cloudwatch_data['NetworkIn'].mean(),
            'network_out': cloudwatch_data['NetworkOut'].mean(),
            'disk_read': cloudwatch_data['DiskReadOps'].mean(),
            'disk_write': cloudwatch_data['DiskWriteOps'].mean(),
        }
        return features
    
    def recommend_instance(self, 
                          current_instance: str,
                          usage_features: Dict,
                          instance_id: str) -> Dict:
        """
        Recommend optimal instance type based on usage.
        
        Returns:
        {
            'current_instance': 'm5.xlarge',
            'recommended_instance': 'm5.large',
            'current_cost': 146.88,
            'recommended_cost': 73.44,
            'monthly_savings': 73.44,
            'savings_percentage': 50.0,
            'cpu_utilization': 15.0,
            'memory_utilization': 25.0,
            'risk_level': 'low',
            'confidence': 95.0,
            'reasoning': 'CPU and memory usage are well below current instance capacity...'
        }
        """
        current_specs = self.INSTANCE_SPECS.get(current_instance)
        if not current_specs:
            return None
        
        # Calculate required resources with 20% headroom
        required_vcpu = max(
            usage_features['cpu_p99'] * current_specs['vCPU'] / 100 * 1.2,
            1  # Minimum 1 vCPU
        )
        required_memory = max(
            usage_features['memory_p99'] * current_specs['memory_gb'] / 100 * 1.2,
            1  # Minimum 1GB
        )
        
        # Find best matching instance
        best_instance = None
        best_cost = float('inf')
        
        for instance_type, specs in self.INSTANCE_SPECS.items():
            # Skip if insufficient resources
            if specs['vCPU'] < required_vcpu or specs['memory_gb'] < required_memory:
                continue
            
            # Skip if larger than current (we want to downsize)
            if specs['vCPU'] > current_specs['vCPU']:
                continue
            
            # Calculate monthly cost
            monthly_cost = specs['price_per_hour'] * 24 * 30
            
            if monthly_cost < best_cost:
                best_cost = monthly_cost
                best_instance = instance_type
        
        if not best_instance:
            return None
        
        # Calculate savings
        current_monthly_cost = current_specs['price_per_hour'] * 24 * 30
        savings = current_monthly_cost - best_cost
        savings_pct = (savings / current_monthly_cost) * 100
        
        # Calculate risk level
        cpu_headroom = (current_specs['vCPU'] - required_vcpu) / current_specs['vCPU'] * 100
        memory_headroom = (current_specs['memory_gb'] - required_memory) / current_specs['memory_gb'] * 100
        
        if cpu_headroom > 30 and memory_headroom > 30:
            risk_level = 'low'
            confidence = 95.0
        elif cpu_headroom > 20 and memory_headroom > 20:
            risk_level = 'medium'
            confidence = 85.0
        else:
            risk_level = 'high'
            confidence = 70.0
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            current_instance, best_instance, usage_features, 
            required_vcpu, required_memory, savings
        )
        
        return {
            'current_instance': current_instance,
            'recommended_instance': best_instance,
            'instance_id': instance_id,
            'current_cost': round(current_monthly_cost, 2),
            'recommended_cost': round(best_cost, 2),
            'monthly_savings': round(savings, 2),
            'savings_percentage': round(savings_pct, 2),
            'cpu_utilization_avg': round(usage_features['cpu_avg'], 2),
            'cpu_utilization_p95': round(usage_features['cpu_p95'], 2),
            'memory_utilization_avg': round(usage_features['memory_avg'], 2),
            'memory_utilization_p95': round(usage_features['memory_p95'], 2),
            'required_vcpu': round(required_vcpu, 2),
            'required_memory_gb': round(required_memory, 2),
            'risk_level': risk_level,
            'confidence': confidence,
            'reasoning': reasoning
        }
    
    def _generate_reasoning(self, current: str, recommended: str, 
                           usage: Dict, req_vcpu: float, 
                           req_mem: float, savings: float) -> str:
        """Generate human-readable reasoning for recommendation."""
        return (
            f"Your {current} instance is using only {usage['cpu_avg']:.1f}% CPU and "
            f"{usage['memory_avg']:.1f}% memory on average. Peak usage (p95) is "
            f"{usage['cpu_p95']:.1f}% CPU and {usage['memory_p95']:.1f}% memory. "
            f"Switching to {recommended} would provide sufficient capacity with "
            f"20% headroom while saving ${savings:.2f}/month ({((savings / (current_specs['price_per_hour'] * 24 * 30)) * 100):.1f}%)."
        )
```

### **API Endpoint**

```python
# api/routers/ml_right_sizing.py

from fastapi import APIRouter, Depends
from sqlmodel import Session
from api.secure.deps import get_session
from api.ml.right_sizing import RightSizingRecommender
from api.secure.aws.cloudwatch import fetch_instance_metrics
import boto3

router = APIRouter(prefix="/api/ml", tags=["ML"])

@router.get("/right-sizing")
async def get_right_sizing_recommendations(
    session: Session = Depends(get_session),
    authorization: str = Header(...)
):
    """
    Get right-sizing recommendations for all EC2 instances.
    """
    # Fetch EC2 instances
    ec2_client = boto3.client('ec2')
    instances = ec2_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    
    recommender = RightSizingRecommender()
    recommendations = []
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            
            # Fetch CloudWatch metrics (last 14 days)
            metrics = await fetch_instance_metrics(instance_id, days=14)
            
            if not metrics:
                continue
            
            # Extract features
            features = recommender.extract_features(metrics)
            
            # Get recommendation
            recommendation = recommender.recommend_instance(
                instance_type, features, instance_id
            )
            
            if recommendation:
                recommendations.append(recommendation)
    
    # Sort by savings
    recommendations.sort(key=lambda x: x['monthly_savings'], reverse=True)
    
    return {
        "recommendations": recommendations,
        "total_potential_savings": sum([r['monthly_savings'] for r in recommendations]),
        "total_recommendations": len(recommendations)
    }
```

---

## 🎯 **MODEL 3: Instance Type Optimization**

### **Architecture**

```python
# api/ml/instance_optimizer.py

class InstanceTypeOptimizer:
    """
    Recommend optimal instance family/type based on workload characteristics.
    """
    
    INSTANCE_FAMILIES = {
        'compute_optimized': ['c5', 'c5n', 'c6i'],
        'memory_optimized': ['r5', 'r5n', 'r6i'],
        'general_purpose': ['m5', 'm5n', 'm6i'],
        'storage_optimized': ['i3', 'i3en'],
        'burstable': ['t3', 't3a']
    }
    
    def classify_workload(self, usage_features: Dict) -> str:
        """
        Classify workload type:
        - compute_intensive: High CPU, low memory
        - memory_intensive: High memory, moderate CPU
        - balanced: Moderate CPU and memory
        - io_intensive: High disk I/O
        """
        cpu_usage = usage_features['cpu_avg']
        memory_usage = usage_features['memory_avg']
        io_usage = (usage_features['disk_read'] + usage_features['disk_write']) / 1000
        
        if cpu_usage > 70 and memory_usage < 40:
            return 'compute_intensive'
        elif memory_usage > 70 and cpu_usage < 40:
            return 'memory_intensive'
        elif io_usage > 100:
            return 'io_intensive'
        else:
            return 'balanced'
    
    def recommend_instance_family(self, 
                                  current_instance: str,
                                  workload_type: str) -> Dict:
        """
        Recommend better instance family based on workload type.
        
        Example:
        - Current: m5.xlarge (general purpose)
        - Workload: compute_intensive
        - Recommendation: c5.xlarge (compute-optimized)
        """
        current_family = current_instance.split('.')[0]
        
        # Map workload to recommended family
        workload_to_family = {
            'compute_intensive': 'compute_optimized',
            'memory_intensive': 'memory_optimized',
            'io_intensive': 'storage_optimized',
            'balanced': 'general_purpose'
        }
        
        recommended_family_type = workload_to_family.get(workload_type, 'general_purpose')
        
        # Get instance size (large, xlarge, etc.)
        instance_size = current_instance.split('.')[1]
        
        # Recommend equivalent instance in optimal family
        recommended_families = self.INSTANCE_FAMILIES.get(recommended_family_type, ['m5'])
        recommended_instance = f"{recommended_families[0]}.{instance_size}"
        
        # Calculate cost and performance benefits
        current_cost = self._get_instance_cost(current_instance)
        recommended_cost = self._get_instance_cost(recommended_instance)
        
        savings = current_cost - recommended_cost
        
        # Estimate performance improvement
        performance_boost = self._estimate_performance_boost(
            current_family, recommended_families[0], workload_type
        )
        
        return {
            'current_instance': current_instance,
            'recommended_instance': recommended_instance,
            'workload_type': workload_type,
            'current_cost': current_cost,
            'recommended_cost': recommended_cost,
            'monthly_savings': savings,
            'performance_improvement_pct': performance_boost,
            'reasoning': f"Your workload is {workload_type.replace('_', ' ')}. "
                        f"Switching from {current_instance} (general purpose) to "
                        f"{recommended_instance} ({recommended_family_type.replace('_', ' ')}) "
                        f"will provide better price/performance with {performance_boost}% performance boost."
        }
```

---

## 📊 **DATA COLLECTION REQUIREMENTS**

### **CloudWatch Metrics Needed:**

1. **EC2 Metrics:**
   - `CPUUtilization` (percent)
   - `MemoryUtilization` (percent) - via custom metric
   - `NetworkIn` (bytes)
   - `NetworkOut` (bytes)
   - `DiskReadOps` (count)
   - `DiskWriteOps` (count)

2. **Cost Data:**
   - Daily cost by service (from CUR)
   - Instance-level costs
   - Reserved Instance usage

3. **Resource Metadata:**
   - Instance types
   - Instance IDs
   - Tags
   - Launch dates

---

## 🚀 **NEXT STEPS**

1. **Implement CloudWatch metrics collection**
2. **Build feature engineering pipeline**
3. **Train MVP anomaly detection model**
4. **Deploy right-sizing recommender**
5. **Create ML recommendations UI**

---

**Status:** Ready for implementation  
**Priority:** 🔴 Critical

