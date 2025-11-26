#!/usr/bin/env python3
"""
Test CloudWatch Metrics Collection
Tests collecting REAL EC2 metrics from AWS account
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from api.secure.aws.cloudwatch import get_ec2_instances, get_cloudwatch_metrics, collect_all_instance_metrics
from api.secure.deps import get_tenant_session_and_meta
from api.auth_onboarding.routes import get_session, engine
from api.auth_onboarding.models import Tenant
from sqlmodel import Session, select
from datetime import datetime, timedelta

def test_cloudwatch_collection():
    """Test CloudWatch metrics collection with real AWS account"""
    print("🧪 Testing CloudWatch Metrics Collection")
    print("=" * 60)
    
    # Get database session
    with Session(engine) as session:
        # Find a tenant with AWS connection
        tenant = session.exec(
            select(Tenant)
            .where(Tenant.aws_role_arn.isnot(None))
            .where(Tenant.external_id.isnot(None))
        ).first()
        
        if not tenant:
            print("❌ No tenant found with AWS connection configured")
            print("\n💡 To test CloudWatch collection:")
            print("   1. Connect a tenant to AWS (via Settings page)")
            print("   2. Make sure AWS role ARN and External ID are set")
            return False
        
        print(f"✅ Found tenant: {tenant.name}")
        print(f"   AWS Role ARN: {tenant.aws_role_arn}")
        print(f"   Region: {tenant.region}")
        
        try:
            # Get AWS session
            session_aws, meta = get_tenant_session_and_meta(tenant.id)
            print(f"\n✅ AWS session created successfully")
            
            # Get EC2 instances
            print("\n📊 Discovering EC2 instances...")
            instances = get_ec2_instances(session_aws)
            
            if not instances:
                print("⚠️  No EC2 instances found in this AWS account")
                print("   This is OK - you can still test with other resources")
                return True
            
            print(f"✅ Found {len(instances)} EC2 instances:")
            for i, instance in enumerate(instances[:5], 1):  # Show first 5
                print(f"   {i}. {instance['instance_id']} ({instance['instance_type']}) - {instance['state']}")
            
            if len(instances) > 5:
                print(f"   ... and {len(instances) - 5} more")
            
            # Test CloudWatch metrics collection for first instance
            if instances:
                test_instance = instances[0]
                instance_id = test_instance['instance_id']
                
                print(f"\n📈 Collecting CloudWatch metrics for {instance_id}...")
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=7)
                
                metrics = get_cloudwatch_metrics(
                    session_aws,
                    instance_id,
                    start_time,
                    end_time,
                    period=3600  # 1 hour periods
                )
                
                print(f"\n✅ Metrics collected:")
                print(f"   CPU Utilization: {len(metrics['cpu_utilization'])} data points")
                print(f"   Network In: {len(metrics['network_in'])} data points")
                print(f"   Network Out: {len(metrics['network_out'])} data points")
                
                if metrics['cpu_utilization']:
                    cpu_values = [dp['value'] for dp in metrics['cpu_utilization']]
                    avg_cpu = sum(cpu_values) / len(cpu_values)
                    print(f"   Average CPU: {avg_cpu:.2f}%")
                
                # Test full collection
                print(f"\n📊 Testing full metrics collection...")
                metrics_df = collect_all_instance_metrics(session_aws, lookback_days=7)
                
                if not metrics_df.empty:
                    print(f"✅ Collected metrics for {len(metrics_df)} data points")
                    print(f"   Instances: {metrics_df['instance_id'].nunique()}")
                    print(f"   Date range: {metrics_df['timestamp'].min()} to {metrics_df['timestamp'].max()}")
                    print(f"\n📋 Sample data:")
                    print(metrics_df.head().to_string())
                    return True
                else:
                    print("⚠️  No metrics collected (instances might be stopped or no metrics available)")
                    return True
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_cloudwatch_collection()
    if success:
        print("\n✅ CloudWatch collection test completed!")
    else:
        print("\n❌ CloudWatch collection test failed")
        sys.exit(1)

