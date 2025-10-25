#!/usr/bin/env python3
"""
Setup CloudWatch Alarms for AWS Cost Optimizer
"""

import boto3
import json

def create_cloudwatch_alarms():
    """Create CloudWatch alarms for monitoring"""
    
    cloudwatch = boto3.client('cloudwatch')
    
    alarms = [
        {
            'AlarmName': 'aws-cost-optimizer-api-high-cpu',
            'AlarmDescription': 'API service high CPU utilization',
            'MetricName': 'CPUUtilization',
            'Namespace': 'AWS/ECS',
            'Statistic': 'Average',
            'Dimensions': [
                {'Name': 'ServiceName', 'Value': 'aws-cost-optimizer-dev-api'},
                {'Name': 'ClusterName', 'Value': 'aws-cost-optimizer-dev-cluster'}
            ],
            'Period': 300,
            'EvaluationPeriods': 2,
            'Threshold': 80.0,
            'ComparisonOperator': 'GreaterThanThreshold',
            'AlarmActions': [],
            'OKActions': []
        },
        {
            'AlarmName': 'aws-cost-optimizer-web-high-cpu',
            'AlarmDescription': 'Web service high CPU utilization',
            'MetricName': 'CPUUtilization',
            'Namespace': 'AWS/ECS',
            'Statistic': 'Average',
            'Dimensions': [
                {'Name': 'ServiceName', 'Value': 'aws-cost-optimizer-dev-web'},
                {'Name': 'ClusterName', 'Value': 'aws-cost-optimizer-dev-cluster'}
            ],
            'Period': 300,
            'EvaluationPeriods': 2,
            'Threshold': 80.0,
            'ComparisonOperator': 'GreaterThanThreshold',
            'AlarmActions': [],
            'OKActions': []
        },
        {
            'AlarmName': 'aws-cost-optimizer-api-high-memory',
            'AlarmDescription': 'API service high memory utilization',
            'MetricName': 'MemoryUtilization',
            'Namespace': 'AWS/ECS',
            'Statistic': 'Average',
            'Dimensions': [
                {'Name': 'ServiceName', 'Value': 'aws-cost-optimizer-dev-api'},
                {'Name': 'ClusterName', 'Value': 'aws-cost-optimizer-dev-cluster'}
            ],
            'Period': 300,
            'EvaluationPeriods': 2,
            'Threshold': 85.0,
            'ComparisonOperator': 'GreaterThanThreshold',
            'AlarmActions': [],
            'OKActions': []
        },
        {
            'AlarmName': 'aws-cost-optimizer-web-high-memory',
            'AlarmDescription': 'Web service high memory utilization',
            'MetricName': 'MemoryUtilization',
            'Namespace': 'AWS/ECS',
            'Statistic': 'Average',
            'Dimensions': [
                {'Name': 'ServiceName', 'Value': 'aws-cost-optimizer-dev-web'},
                {'Name': 'ClusterName', 'Value': 'aws-cost-optimizer-dev-cluster'}
            ],
            'Period': 300,
            'EvaluationPeriods': 2,
            'Threshold': 85.0,
            'ComparisonOperator': 'GreaterThanThreshold',
            'AlarmActions': [],
            'OKActions': []
        },
        {
            'AlarmName': 'aws-cost-optimizer-alb-high-5xx',
            'AlarmDescription': 'ALB high 5xx error rate',
            'MetricName': 'HTTPCode_Target_5XX_Count',
            'Namespace': 'AWS/ApplicationELB',
            'Statistic': 'Sum',
            'Dimensions': [
                {'Name': 'LoadBalancer', 'Value': 'app/aws-cost-optimizer-dev-alb/2097253605'}
            ],
            'Period': 300,
            'EvaluationPeriods': 2,
            'Threshold': 10.0,
            'ComparisonOperator': 'GreaterThanThreshold',
            'AlarmActions': [],
            'OKActions': []
        }
    ]
    
    created_alarms = []
    failed_alarms = []
    
    for alarm in alarms:
        try:
            response = cloudwatch.put_metric_alarm(**alarm)
            created_alarms.append(alarm['AlarmName'])
            print(f"✅ Created alarm: {alarm['AlarmName']}")
        except Exception as e:
            failed_alarms.append(alarm['AlarmName'])
            print(f"❌ Failed to create alarm {alarm['AlarmName']}: {e}")
    
    print(f"\n📊 Alarm Summary:")
    print(f"✅ Created: {len(created_alarms)} alarms")
    print(f"❌ Failed: {len(failed_alarms)} alarms")
    
    if created_alarms:
        print(f"\nCreated alarms: {', '.join(created_alarms)}")
    
    if failed_alarms:
        print(f"\nFailed alarms: {', '.join(failed_alarms)}")
    
    return len(failed_alarms) == 0

if __name__ == "__main__":
    create_cloudwatch_alarms()
