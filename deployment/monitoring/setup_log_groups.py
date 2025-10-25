#!/usr/bin/env python3
"""
Setup CloudWatch Log Groups for AWS Cost Optimizer
"""

import boto3
import json

def setup_log_groups():
    """Setup CloudWatch log groups with proper retention"""
    
    logs = boto3.client('logs')
    
    log_groups = [
        {
            'logGroupName': '/ecs/aws-cost-optimizer-dev-api',
            'retentionInDays': 30
        },
        {
            'logGroupName': '/ecs/aws-cost-optimizer-dev-web',
            'retentionInDays': 30
        },
        {
            'logGroupName': '/aws/lambda/etl-aws-cur-parser',
            'retentionInDays': 14
        },
        {
            'logGroupName': '/aws/lambda/signal-router',
            'retentionInDays': 14
        }
    ]
    
    created_groups = []
    updated_groups = []
    failed_groups = []
    
    for log_group in log_groups:
        try:
            # Try to create the log group
            try:
                logs.create_log_group(logGroupName=log_group['logGroupName'])
                created_groups.append(log_group['logGroupName'])
                print(f"✅ Created log group: {log_group['logGroupName']}")
            except logs.exceptions.ResourceAlreadyExistsException:
                # Log group already exists, update retention
                updated_groups.append(log_group['logGroupName'])
                print(f"📝 Log group already exists: {log_group['logGroupName']}")
            
            # Set retention policy
            logs.put_retention_policy(
                logGroupName=log_group['logGroupName'],
                retentionInDays=log_group['retentionInDays']
            )
            print(f"📅 Set retention to {log_group['retentionInDays']} days for {log_group['logGroupName']}")
            
        except Exception as e:
            failed_groups.append(log_group['logGroupName'])
            print(f"❌ Failed to setup log group {log_group['logGroupName']}: {e}")
    
    print(f"\n📊 Log Group Summary:")
    print(f"✅ Created: {len(created_groups)} log groups")
    print(f"📝 Updated: {len(updated_groups)} log groups")
    print(f"❌ Failed: {len(failed_groups)} log groups")
    
    if created_groups:
        print(f"\nCreated log groups: {', '.join(created_groups)}")
    
    if updated_groups:
        print(f"\nUpdated log groups: {', '.join(updated_groups)}")
    
    if failed_groups:
        print(f"\nFailed log groups: {', '.join(failed_groups)}")
    
    return len(failed_groups) == 0

if __name__ == "__main__":
    setup_log_groups()
