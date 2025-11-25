"""
Feature Engineering Pipeline
Extract and transform features for ML models from AWS cost and usage data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def extract_cost_features(cost_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract features from cost data for anomaly detection and forecasting.
    
    Args:
        cost_data: DataFrame with columns: date, cost, service (optional)
    
    Returns:
        DataFrame with extracted features
    """
    df = cost_data.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Daily cost
    df['daily_cost'] = df['cost']
    
    # Day-over-day change
    df['cost_change'] = df['cost'].diff()
    df['cost_change_pct'] = df['cost'].pct_change() * 100
    
    # Rolling statistics (7-day window)
    df['rolling_mean_7d'] = df['cost'].rolling(window=7, min_periods=1).mean()
    df['rolling_std_7d'] = df['cost'].rolling(window=7, min_periods=1).std()
    
    # Rolling statistics (30-day window)
    df['rolling_mean_30d'] = df['cost'].rolling(window=30, min_periods=1).mean()
    df['rolling_std_30d'] = df['cost'].rolling(window=30, min_periods=1).std()
    
    # Z-score (how many standard deviations from mean)
    df['z_score'] = (df['cost'] - df['rolling_mean_7d']) / (df['rolling_std_7d'] + 1e-6)
    
    # Day of week (0=Monday, 6=Sunday)
    df['day_of_week'] = df['date'].dt.dayofweek
    
    # Day of month
    df['day_of_month'] = df['date'].dt.day
    
    # Month
    df['month'] = df['date'].dt.month
    
    # Year
    df['year'] = df['date'].dt.year
    
    # Is weekend
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Lag features (previous day's cost)
    df['cost_lag_1'] = df['cost'].shift(1)
    df['cost_lag_7'] = df['cost'].shift(7)
    df['cost_lag_30'] = df['cost'].shift(30)
    
    # Fill NaN values (using forward fill then backward fill)
    df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
    
    return df


def extract_utilization_features(metrics_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract features from CloudWatch utilization metrics for right-sizing.
    
    Args:
        metrics_data: DataFrame with columns: instance_id, timestamp, cpu_utilization, memory_utilization, network_in, network_out
    
    Returns:
        DataFrame with extracted features
    """
    df = metrics_data.copy()
    
    # Aggregate metrics per instance
    instance_features = df.groupby('instance_id').agg({
        'cpu_utilization': ['mean', 'std', 'min', 'max', lambda x: np.percentile(x, 95), lambda x: np.percentile(x, 99)],
        'memory_utilization': ['mean', 'std', 'min', 'max', lambda x: np.percentile(x, 95), lambda x: np.percentile(x, 99)],
        'network_in': ['mean', 'max'],
        'network_out': ['mean', 'max']
    }).reset_index()
    
    # Flatten column names
    instance_features.columns = ['instance_id', 
                                 'cpu_mean', 'cpu_std', 'cpu_min', 'cpu_max', 'cpu_p95', 'cpu_p99',
                                 'memory_mean', 'memory_std', 'memory_min', 'memory_max', 'memory_p95', 'memory_p99',
                                 'network_in_mean', 'network_in_max',
                                 'network_out_mean', 'network_out_max']
    
    # Calculate utilization ratios
    instance_features['cpu_utilization_ratio'] = instance_features['cpu_mean'] / 100.0
    instance_features['memory_utilization_ratio'] = instance_features['memory_mean'] / 100.0
    
    # Calculate peak to average ratios
    instance_features['cpu_peak_to_avg'] = instance_features['cpu_max'] / (instance_features['cpu_mean'] + 1e-6)
    instance_features['memory_peak_to_avg'] = instance_features['memory_max'] / (instance_features['memory_mean'] + 1e-6)
    
    return instance_features


def prepare_anomaly_features(cost_data: pd.DataFrame, lookback_days: int = 90) -> np.ndarray:
    """
    Prepare feature matrix for anomaly detection model.
    
    Args:
        cost_data: DataFrame with cost data
        lookback_days: Number of days to use for feature extraction
    
    Returns:
        Feature matrix (n_samples, n_features)
    """
    # Filter to last N days
    cutoff_date = cost_data['date'].max() - timedelta(days=lookback_days)
    recent_data = cost_data[cost_data['date'] >= cutoff_date].copy()
    
    # Extract features
    features_df = extract_cost_features(recent_data)
    
    # Select feature columns
    feature_cols = [
        'daily_cost',
        'cost_change',
        'cost_change_pct',
        'rolling_mean_7d',
        'rolling_std_7d',
        'z_score',
        'day_of_week',
        'is_weekend',
        'cost_lag_1',
        'cost_lag_7'
    ]
    
    # Create feature matrix
    feature_matrix = features_df[feature_cols].values
    
    return feature_matrix


def prepare_rightsizing_features(metrics_data: pd.DataFrame) -> np.ndarray:
    """
    Prepare feature matrix for right-sizing model.
    
    Args:
        metrics_data: DataFrame with CloudWatch metrics
    
    Returns:
        Feature matrix (n_instances, n_features)
    """
    # Extract utilization features
    features_df = extract_utilization_features(metrics_data)
    
    # Select feature columns
    feature_cols = [
        'cpu_mean', 'cpu_p95', 'cpu_p99',
        'memory_mean', 'memory_p95', 'memory_p99',
        'cpu_utilization_ratio',
        'memory_utilization_ratio',
        'cpu_peak_to_avg',
        'memory_peak_to_avg'
    ]
    
    # Create feature matrix
    feature_matrix = features_df[feature_cols].values
    
    return feature_matrix

