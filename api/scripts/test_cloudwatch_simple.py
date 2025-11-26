#!/usr/bin/env python3
"""
Simple CloudWatch Test - Tests CloudWatch collection without FastAPI dependencies
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from api.secure.aws.cloudwatch import get_ec2_instances, get_cloudwatch_metrics
from api.secure.aws.assume_role import assume_vendor_role
from datetime import datetime, timedelta

def test_cloudwatch_simple():
    """Test CloudWatch collection with manual AWS credentials"""
    print("🧪 Testing CloudWatch Metrics Collection")
    print("=" * 60)
    
    # Check for AWS credentials
    aws_role_arn = os.getenv("AWS_ROLE_ARN")
    external_id = os.getenv("AWS_EXTERNAL_ID")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    if not aws_role_arn or not external_id:
        print("⚠️  AWS credentials not found in environment")
        print("\n💡 To test CloudWatch collection:")
        print("   1. Set AWS_ROLE_ARN environment variable")
        print("   2. Set AWS_EXTERNAL_ID environment variable")
        print("   3. Set AWS_REGION (optional, defaults to us-east-1)")
        print("\n   Or connect a tenant via the web UI first")
        return False
    
    try:
        # Assume AWS role
        print(f"🔐 Assuming AWS role: {aws_role_arn}")
        session = assume_vendor_role(aws_role_arn, external_id, region)
        print("✅ AWS session created successfully")
        
        # Get EC2 instances
        print("\n📊 Discovering EC2 instances...")
        instances = get_ec2_instances(session)
        
        if not instances:
            print("⚠️  No EC2 instances found in this AWS account")
            print("   This is OK - you can still test with other resources")
            return True
        
        print(f"✅ Found {len(instances)} EC2 instances:")
        for i, instance in enumerate(instances[:5], 1):
            print(f"   {i}. {instance['instance_id']} ({instance['instance_type']}) - {instance['state']}")
        
        if len(instances) > 5:
            print(f"   ... and {len(instances) - 5} more")
        
        # Test CloudWatch metrics for first running instance
        running_instances = [i for i in instances if i['state'] == 'running']
        
        if running_instances:
            test_instance = running_instances[0]
            instance_id = test_instance['instance_id']
            
            print(f"\n📈 Collecting CloudWatch metrics for {instance_id}...")
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            
            metrics = get_cloudwatch_metrics(
                session,
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
                max_cpu = max(cpu_values)
                print(f"   Average CPU: {avg_cpu:.2f}%")
                print(f"   Max CPU: {max_cpu:.2f}%")
            
            return True
        else:
            print("⚠️  No running instances found to test metrics collection")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cloudwatch_simple()
    if success:
        print("\n✅ CloudWatch collection test completed!")
        print("\n💡 Next: Test with your real AWS account via the web UI")
    else:
        print("\n❌ CloudWatch collection test failed")
        print("\n💡 Make sure:")
        print("   1. AWS credentials are configured")
        print("   2. Tenant is connected via web UI")
        print("   3. IAM role has CloudWatch read permissions")


