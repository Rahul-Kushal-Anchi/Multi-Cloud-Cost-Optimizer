#!/usr/bin/env python3
"""
Setup X-Ray Tracing for AWS Cost Optimizer
"""

import boto3
import json

def setup_xray_tracing():
    """Setup X-Ray tracing for distributed monitoring"""
    
    xray = boto3.client('xray')
    
    try:
        # Create sampling rule for the application
        sampling_rule = {
            'RuleName': 'aws-cost-optimizer-sampling-rule',
            'Priority': 1,
            'FixedRate': 0.1,  # Sample 10% of requests
            'ReservoirSize': 10,
            'ServiceName': 'aws-cost-optimizer',
            'ServiceType': 'AWS::ECS::Service',
            'Host': '*',
            'HTTPMethod': '*',
            'URLPath': '*',
            'ResourceARN': '*',
            'Version': 1
        }
        
        # Create the sampling rule
        response = xray.create_sampling_rule(
            SamplingRule=sampling_rule
        )
        print("✅ X-Ray sampling rule created successfully")
        print(f"Rule ARN: {response['SamplingRuleRecord']['SamplingRule']['RuleARN']}")
        
        # Create group for cost optimization traces
        group_config = {
            'GroupName': 'aws-cost-optimizer-traces',
            'FilterExpression': 'service("aws-cost-optimizer")',
            'InsightsConfiguration': {
                'InsightsEnabled': True,
                'NotificationsEnabled': True
            }
        }
        
        try:
            xray.create_group(**group_config)
            print("✅ X-Ray group created successfully")
        except xray.exceptions.InvalidRequestException as e:
            if "already exists" in str(e):
                print("📝 X-Ray group already exists")
            else:
                raise e
        
        print("\n🔍 X-Ray Setup Complete!")
        print("X-Ray Console: https://us-east-1.console.aws.amazon.com/xray/home?region=us-east-1#/traces")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up X-Ray tracing: {e}")
        return False

if __name__ == "__main__":
    setup_xray_tracing()
