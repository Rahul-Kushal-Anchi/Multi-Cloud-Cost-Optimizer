#!/usr/bin/env python3
"""
Setup CloudWatch Dashboard for AWS Cost Optimizer
"""

import boto3
import json
from datetime import datetime

def create_cloudwatch_dashboard():
    """Create CloudWatch dashboard for monitoring"""
    
    cloudwatch = boto3.client('cloudwatch')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/ECS", "CPUUtilization", "ServiceName", "aws-cost-optimizer-dev-api", "ClusterName", "aws-cost-optimizer-dev-cluster"],
                        [".", "CPUUtilization", ".", "aws-cost-optimizer-dev-web", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "ECS Service CPU Utilization",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/ECS", "MemoryUtilization", "ServiceName", "aws-cost-optimizer-dev-api", "ClusterName", "aws-cost-optimizer-dev-cluster"],
                        [".", "MemoryUtilization", ".", "aws-cost-optimizer-dev-web", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "ECS Service Memory Utilization",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 0,
                "y": 6,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "aws-cost-optimizer-dev-alb-2097253605"],
                        [".", "RequestCount", ".", "."],
                        [".", "HTTPCode_Target_2XX_Count", ".", "."],
                        [".", "HTTPCode_Target_4XX_Count", ".", "."],
                        [".", "HTTPCode_Target_5XX_Count", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "ALB Metrics",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 6,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/Logs", "IncomingLogEvents", "LogGroupName", "/ecs/aws-cost-optimizer-dev-api"],
                        [".", "IncomingBytes", ".", "."],
                        [".", "IncomingLogEvents", ".", "/ecs/aws-cost-optimizer-dev-web"],
                        [".", "IncomingBytes", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "Application Logs",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 0,
                "y": 12,
                "width": 24,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/ECS", "RunningTaskCount", "ServiceName", "aws-cost-optimizer-dev-api", "ClusterName", "aws-cost-optimizer-dev-cluster"],
                        [".", "RunningTaskCount", ".", "aws-cost-optimizer-dev-web", ".", "."],
                        [".", "PendingTaskCount", ".", "aws-cost-optimizer-dev-api", ".", "."],
                        [".", "PendingTaskCount", ".", "aws-cost-optimizer-dev-web", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "ECS Task Status",
                    "period": 300
                }
            }
        ]
    }
    
    try:
        response = cloudwatch.put_dashboard(
            DashboardName='AWS-Cost-Optimizer-Dashboard',
            DashboardBody=json.dumps(dashboard_body)
        )
        print("✅ CloudWatch Dashboard created successfully")
        print(f"Dashboard URL: https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=AWS-Cost-Optimizer-Dashboard")
        return True
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return False

if __name__ == "__main__":
    create_cloudwatch_dashboard()
