"""
ML Model Database Schema
SQLModel definitions for ML models, anomalies, and recommendations
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class MLModel(SQLModel, table=True):
    """ML Model registry - tracks trained models"""
    __tablename__ = "ml_models"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    model_type: str  # 'anomaly_detection', 'right_sizing', 'forecasting'
    version: str  # Model version (e.g., '1.0.0')
    trained_at: datetime = Field(default_factory=datetime.utcnow)
    accuracy: Optional[float] = None  # Model accuracy score
    model_path: Optional[str] = None  # Path to saved model (S3 or local)
    training_data_start: Optional[datetime] = None  # Start date of training data
    training_data_end: Optional[datetime] = None  # End date of training data
    training_data_days: Optional[int] = None  # Number of days of training data
    hyperparameters: Optional[str] = None  # JSON string of hyperparameters
    is_active: bool = Field(default=True)  # Whether this is the active model
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Anomaly(SQLModel, table=True):
    """Anomaly detection results"""
    __tablename__ = "anomalies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    anomaly_date: datetime  # Date when anomaly occurred
    anomaly_score: float  # ML model anomaly score (0-100)
    anomaly_type: str  # 'spike', 'drop', 'pattern_change', 'unusual_pattern'
    severity: str  # 'low', 'medium', 'high', 'critical'
    affected_service: Optional[str] = None  # AWS service name
    affected_resource: Optional[str] = None  # Resource ID (e.g., instance ID)
    estimated_impact: Optional[Decimal] = None  # Estimated cost impact in USD
    cost_before: Optional[Decimal] = None  # Cost before anomaly
    cost_after: Optional[Decimal] = None  # Cost after anomaly
    root_cause: Optional[str] = None  # Root cause analysis
    status: str = Field(default="detected")  # 'detected', 'investigating', 'resolved', 'false_positive'
    model_version: Optional[str] = None  # Version of model that detected this
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Recommendation(SQLModel, table=True):
    """Right-sizing recommendations"""
    __tablename__ = "recommendations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    resource_id: str  # EC2 instance ID or other resource ID
    resource_type: str = "ec2"  # 'ec2', 'rds', etc.
    current_instance_type: str  # Current instance type (e.g., 'm5.xlarge')
    recommended_instance_type: str  # Recommended instance type (e.g., 'm5.large')
    current_monthly_cost: Decimal  # Current monthly cost in USD
    recommended_monthly_cost: Decimal  # Recommended monthly cost in USD
    estimated_savings: Decimal  # Monthly savings in USD
    savings_percentage: float  # Percentage savings (0-100)
    risk_level: str  # 'low', 'medium', 'high'
    confidence_score: float  # ML model confidence (0-100)
    reasoning: Optional[str] = None  # Explanation of recommendation
    cpu_utilization_avg: Optional[float] = None  # Average CPU utilization %
    cpu_utilization_p95: Optional[float] = None  # P95 CPU utilization %
    memory_utilization_avg: Optional[float] = None  # Average memory utilization %
    memory_utilization_p95: Optional[float] = None  # P95 memory utilization %
    status: str = Field(default="pending")  # 'pending', 'approved', 'applied', 'rejected'
    applied_at: Optional[datetime] = None  # When recommendation was applied
    model_version: Optional[str] = None  # Version of model that generated this
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Forecast(SQLModel, table=True):
    """Cost forecasting results"""
    __tablename__ = "forecasts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    forecast_date: datetime  # Date being forecasted
    forecasted_cost: Decimal  # Forecasted cost in USD
    confidence_lower: Decimal  # Lower bound of confidence interval
    confidence_upper: Decimal  # Upper bound of confidence interval
    confidence_level: float = 0.95  # Confidence level (e.g., 0.95 for 95%)
    trend: str  # 'increasing', 'decreasing', 'stable'
    key_drivers: Optional[str] = None  # JSON string of key cost drivers
    model_version: Optional[str] = None  # Version of model that generated this
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InstanceMetrics(SQLModel, table=True):
    """Stored CloudWatch metrics for EC2 instances"""
    __tablename__ = "instance_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    instance_id: str  # EC2 instance ID
    instance_type: str  # EC2 instance type
    timestamp: datetime  # Metric timestamp
    cpu_utilization: Optional[float] = None  # CPU utilization %
    memory_utilization: Optional[float] = None  # Memory utilization %
    network_in: Optional[float] = None  # Network bytes in
    network_out: Optional[float] = None  # Network bytes out
    disk_read_ops: Optional[float] = None  # Disk read operations
    disk_write_ops: Optional[float] = None  # Disk write operations
    created_at: datetime = Field(default_factory=datetime.utcnow)

