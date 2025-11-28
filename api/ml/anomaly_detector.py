"""
Anomaly Detection Model
ML-powered cost anomaly detection using Isolation Forest
Detects cost spikes, drops, and unusual patterns in AWS spending
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pickle
import os
import logging

try:
    from api.ml.features import extract_cost_features, prepare_anomaly_features
    from api.auth_onboarding.models import Tenant
    from api.ml.models import MLModel, Anomaly
except ImportError:
    from ml.features import extract_cost_features, prepare_anomaly_features
    from auth_onboarding.models import Tenant
    from ml.models import MLModel, Anomaly

logger = logging.getLogger("api.ml.anomaly_detector")


class CostAnomalyDetector:
    """
    ML-based anomaly detection for cost spikes and unusual patterns
    Uses Isolation Forest for unsupervised anomaly detection
    """
    
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        Initialize anomaly detector
        
        Args:
            contamination: Expected proportion of anomalies (default: 0.1 = 10%)
            random_state: Random seed for reproducibility
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
            max_samples='auto',
            bootstrap=False
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_date = None
        self.feature_names = []
        
    def train(self, cost_data: pd.DataFrame, lookback_days: int = 90) -> Dict[str, any]:
        """
        Train the anomaly detection model on historical cost data
        
        Args:
            cost_data: DataFrame with columns [date, cost, service (optional)]
            lookback_days: Number of days to use for training
        
        Returns:
            Training summary with metrics
        """
        logger.info(f"Training anomaly detector on {len(cost_data)} days of data")
        
        # Extract features
        features_df = extract_cost_features(cost_data)
        feature_matrix = prepare_anomaly_features(cost_data, lookback_days)
        
        # Store feature names for later
        self.feature_names = [
            'daily_cost', 'cost_change', 'cost_change_pct',
            'rolling_mean_7d', 'rolling_std_7d', 'z_score',
            'day_of_week', 'is_weekend', 'cost_lag_1', 'cost_lag_7'
        ]
        
        # Scale features
        feature_matrix_scaled = self.scaler.fit_transform(feature_matrix)
        
        # Train model
        self.model.fit(feature_matrix_scaled)
        self.is_trained = True
        self.training_date = datetime.utcnow()
        
        # Calculate anomaly scores on training data
        anomaly_scores = self.model.decision_function(feature_matrix_scaled)
        predictions = self.model.predict(feature_matrix_scaled)
        
        # Count anomalies
        num_anomalies = np.sum(predictions == -1)
        num_normal = np.sum(predictions == 1)
        
        logger.info(f"Training complete: {num_anomalies} anomalies, {num_normal} normal")
        
        return {
            "training_samples": len(cost_data),
            "num_anomalies": int(num_anomalies),
            "num_normal": int(num_normal),
            "contamination_rate": float(num_anomalies / len(cost_data)),
            "training_date": self.training_date.isoformat(),
            "lookback_days": lookback_days,
        }
    
    def detect_anomalies(
        self, 
        cost_data: pd.DataFrame,
        threshold: float = -0.1
    ) -> List[Dict[str, any]]:
        """
        Detect anomalies in cost data
        
        Args:
            cost_data: DataFrame with columns [date, cost, service (optional)]
            threshold: Anomaly score threshold (lower = more anomalous)
        
        Returns:
            List of detected anomalies with details
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before detecting anomalies")
        
        logger.info(f"Detecting anomalies in {len(cost_data)} days of data")
        
        # Extract features
        features_df = extract_cost_features(cost_data)
        feature_matrix = prepare_anomaly_features(cost_data, lookback_days=min(90, len(cost_data)))
        
        # Scale features
        feature_matrix_scaled = self.scaler.transform(feature_matrix)
        
        # Get anomaly scores and predictions
        anomaly_scores = self.model.decision_function(feature_matrix_scaled)
        predictions = self.model.predict(feature_matrix_scaled)
        
        # Identify anomalies
        anomalies = []
        for i, (score, pred) in enumerate(zip(anomaly_scores, predictions)):
            if pred == -1 or score < threshold:
                # This is an anomaly
                date = cost_data.iloc[i]['date']
                cost = cost_data.iloc[i]['cost']
                
                # Determine anomaly type and severity
                if i > 0:
                    prev_cost = cost_data.iloc[i-1]['cost']
                    cost_change_pct = ((cost - prev_cost) / prev_cost * 100) if prev_cost > 0 else 0
                else:
                    cost_change_pct = 0
                
                anomaly_type = self._classify_anomaly_type(cost, cost_change_pct)
                severity = self._calculate_severity(score, cost_change_pct)
                
                anomalies.append({
                    "date": date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else str(date),
                    "cost": float(cost),
                    "anomaly_score": float(score),
                    "anomaly_type": anomaly_type,
                    "severity": severity,
                    "cost_change_pct": float(cost_change_pct) if not np.isnan(cost_change_pct) else 0.0,
                })
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def _classify_anomaly_type(self, cost: float, cost_change_pct: float) -> str:
        """Classify the type of anomaly"""
        if cost_change_pct > 50:
            return "spike"
        elif cost_change_pct < -30:
            return "drop"
        else:
            return "unusual_pattern"
    
    def _calculate_severity(self, anomaly_score: float, cost_change_pct: float) -> str:
        """Calculate severity level of anomaly"""
        if anomaly_score < -0.3 or abs(cost_change_pct) > 100:
            return "critical"
        elif anomaly_score < -0.2 or abs(cost_change_pct) > 50:
            return "high"
        elif anomaly_score < -0.1 or abs(cost_change_pct) > 25:
            return "medium"
        else:
            return "low"
    
    def save_model(self, filepath: str) -> None:
        """Save trained model to file"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'training_date': self.training_date,
            'feature_names': self.feature_names,
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load trained model from file"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.training_date = model_data.get('training_date')
        self.feature_names = model_data.get('feature_names', [])
        self.is_trained = True
        
        logger.info(f"Model loaded from {filepath}")


# Singleton instance
anomaly_detector = CostAnomalyDetector()


