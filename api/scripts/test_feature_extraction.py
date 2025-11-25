#!/usr/bin/env python3
"""
Test Feature Extraction
Tests feature extraction with REAL cost data from Athena
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from api.ml.features import extract_cost_features, prepare_anomaly_features
from api.secure.aws.athena_costs import run_athena_query, cur_cost_query_sql
from api.secure.deps import get_tenant_session_and_meta
from api.auth_onboarding.routes import get_session, engine
from api.auth_onboarding.models import Tenant
from sqlmodel import Session, select
import pandas as pd
from datetime import datetime, timedelta

def test_feature_extraction():
    """Test feature extraction with real cost data"""
    print("🧪 Testing Feature Extraction with REAL Cost Data")
    print("=" * 60)
    
    # Get database session
    with Session(engine) as session:
        # Find a tenant with AWS connection
        tenant = session.exec(
            select(Tenant)
            .where(Tenant.aws_role_arn.isnot(None))
            .where(Tenant.athena_db.isnot(None))
            .where(Tenant.athena_table.isnot(None))
        ).first()
        
        if not tenant:
            print("❌ No tenant found with Athena/CUR connection configured")
            print("\n💡 To test feature extraction:")
            print("   1. Connect a tenant to AWS CUR (via Settings page)")
            print("   2. Make sure Athena database and table are configured")
            return False
        
        print(f"✅ Found tenant: {tenant.name}")
        print(f"   Athena DB: {tenant.athena_db}")
        print(f"   Athena Table: {tenant.athena_table}")
        
        try:
            # Get AWS session
            session_aws, meta = get_tenant_session_and_meta(tenant.id)
            print(f"\n✅ AWS session created successfully")
            
            # Query REAL cost data from Athena (last 90 days)
            print("\n📊 Querying REAL cost data from Athena (last 90 days)...")
            
            # Query daily costs
            query = f"""
            SELECT
              date(line_item_usage_start_date) AS date,
              SUM(CAST(line_item_unblended_cost AS double)) AS cost
            FROM {meta['athena_table']}
            WHERE line_item_usage_start_date >= date_add('day', -90, current_timestamp)
              AND "$path" LIKE '%.parquet'
            GROUP BY date(line_item_usage_start_date)
            ORDER BY date ASC
            """
            
            print("   Running Athena query...")
            results = run_athena_query(
                session_aws,
                query,
                meta['athena_db'],
                meta['athena_workgroup'],
                meta.get('athena_results_bucket'),
                meta.get('athena_results_prefix')
            )
            
            if not results or len(results) == 0:
                print("⚠️  No cost data found in Athena")
                print("   This might mean:")
                print("   - CUR data hasn't been generated yet")
                print("   - Date range has no data")
                print("   - Table/query issue")
                return False
            
            print(f"✅ Retrieved {len(results)} days of REAL cost data")
            
            # Convert to DataFrame
            cost_data = pd.DataFrame(results)
            cost_data['date'] = pd.to_datetime(cost_data['date'])
            cost_data = cost_data.sort_values('date')
            
            print(f"\n📈 Cost Data Summary:")
            print(f"   Date range: {cost_data['date'].min()} to {cost_data['date'].max()}")
            print(f"   Total days: {len(cost_data)}")
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
            print(features_df[['date', 'daily_cost', 'cost_change', 'rolling_mean_7d', 'z_score']].tail().to_string())
            
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
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_feature_extraction()
    if success:
        print("\n✅ Feature extraction test completed!")
        print("\n🎉 Ready to train ML models with REAL data!")
    else:
        print("\n❌ Feature extraction test failed")
        sys.exit(1)

