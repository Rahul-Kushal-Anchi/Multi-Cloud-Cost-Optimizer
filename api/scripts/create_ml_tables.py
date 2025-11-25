#!/usr/bin/env python3
"""
Create ML database tables
Run this script to create ML tables: ml_models, anomalies, recommendations, forecasts, instance_metrics
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlmodel import SQLModel, create_engine
from api.auth_onboarding.models import Tenant, User, UserSettings, Invite, AuditLog
from api.ml.models import MLModel, Anomaly, Recommendation, Forecast, InstanceMetrics

# Get database URL from environment (same as routes.py)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./saas.db"  # Default to SQLite for local development
)

def create_ml_tables():
    """Create all ML-related database tables"""
    print("🔧 Creating ML database tables...")
    print(f"📊 Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Create all tables
    print("\n📋 Creating tables:")
    print("   - ml_models")
    print("   - anomalies")
    print("   - recommendations")
    print("   - forecasts")
    print("   - instance_metrics")
    
    SQLModel.metadata.create_all(engine)
    
    print("\n✅ ML tables created successfully!")
    print("\n💡 Next steps:")
    print("   1. Test CloudWatch metrics collection")
    print("   2. Verify feature extraction works")
    print("   3. Start training ML models")

if __name__ == "__main__":
    create_ml_tables()

