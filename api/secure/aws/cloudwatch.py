"""
CloudWatch Metrics Collection
Collect REAL EC2 instance metrics from AWS CloudWatch
"""

import boto3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from botocore.exceptions import ClientError


def get_ec2_instances(session: boto3.Session) -> List[Dict]:
    """
    Get all EC2 instances from AWS account.
    
    Args:
        session: Boto3 session with assumed role credentials
    
    Returns:
        List of instance dictionaries with instance_id, instance_type, etc.
    """
    ec2 = session.client('ec2')
    
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
            ]
        )
        
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'instance_id': instance['InstanceId'],
                    'instance_type': instance.get('InstanceType', 'unknown'),
                    'state': instance['State']['Name'],
                    'launch_time': instance.get('LaunchTime'),
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                })
        
        return instances
    
    except ClientError as e:
        print(f"Error fetching EC2 instances: {e}")
        return []


def get_cloudwatch_metrics(
    session: boto3.Session,
    instance_id: str,
    start_time: datetime,
    end_time: datetime,
    period: int = 3600  # 1 hour periods
) -> Dict[str, List[Dict]]:
    """
    Get CloudWatch metrics for a specific EC2 instance.
    
    Args:
        session: Boto3 session with assumed role credentials
        instance_id: EC2 instance ID
        start_time: Start time for metrics
        end_time: End time for metrics
        period: Period in seconds (default: 1 hour)
    
    Returns:
        Dictionary with metric names as keys and lists of dicts with 'timestamp' and 'value' as values
    """
    cloudwatch = session.client('cloudwatch')
    
    metrics = {
        'cpu_utilization': [],
        'memory_utilization': [],
        'network_in': [],
        'network_out': [],
        'disk_read_ops': [],
        'disk_write_ops': []
    }
    
    # CPU Utilization
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average', 'Maximum']
        )
        
        if response['Datapoints']:
            sorted_dps = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
            metrics['cpu_utilization'] = [
                {'timestamp': dp['Timestamp'], 'value': dp['Average']}
                for dp in sorted_dps
            ]
    except ClientError as e:
        print(f"Error fetching CPU metrics for {instance_id}: {e}")
    
    # Network In
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkIn',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average', 'Sum']
        )
        
        if response['Datapoints']:
            sorted_dps = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
            metrics['network_in'] = [
                {'timestamp': dp['Timestamp'], 'value': dp['Average']}
                for dp in sorted_dps
            ]
    except ClientError as e:
        print(f"Error fetching NetworkIn metrics for {instance_id}: {e}")
    
    # Network Out
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkOut',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average', 'Sum']
        )
        
        if response['Datapoints']:
            sorted_dps = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
            metrics['network_out'] = [
                {'timestamp': dp['Timestamp'], 'value': dp['Average']}
                for dp in sorted_dps
            ]
    except ClientError as e:
        print(f"Error fetching NetworkOut metrics for {instance_id}: {e}")
    
    # Note: Memory utilization is not available by default in CloudWatch
    # We'll need to use custom metrics or estimate based on instance type
    # For now, we'll leave it empty and handle it separately
    
    return metrics


def collect_all_instance_metrics(
    session: boto3.Session,
    lookback_days: int = 7
) -> pd.DataFrame:
    """
    Collect CloudWatch metrics for all EC2 instances.
    
    Args:
        session: Boto3 session with assumed role credentials
        lookback_days: Number of days to look back for metrics
    
    Returns:
        DataFrame with columns: instance_id, timestamp, cpu_utilization, memory_utilization, network_in, network_out
    """
    # Get all EC2 instances
    instances = get_ec2_instances(session)
    
    if not instances:
        print("No EC2 instances found")
        return pd.DataFrame()
    
    print(f"Found {len(instances)} EC2 instances")
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=lookback_days)
    
    all_metrics = []
    
    for instance in instances:
        instance_id = instance['instance_id']
        print(f"Collecting metrics for {instance_id}...")
        
        # Get CloudWatch metrics (now returns dicts with timestamp and value)
        metrics = get_cloudwatch_metrics(session, instance_id, start_time, end_time)
        
        # Collect all unique timestamps from all metrics
        all_timestamps = set()
        for metric_name, metric_data in metrics.items():
            if metric_data:
                for dp in metric_data:
                    all_timestamps.add(dp['timestamp'])
        
        if not all_timestamps:
            continue
        
        # Sort timestamps
        sorted_timestamps = sorted(all_timestamps)
        
        # Create a lookup dictionary for each metric by timestamp
        metric_lookup = {}
        for metric_name in ['cpu_utilization', 'network_in', 'network_out']:
            metric_lookup[metric_name] = {
                dp['timestamp']: dp['value']
                for dp in metrics.get(metric_name, [])
            }
        
        # Create rows for each timestamp
        for timestamp in sorted_timestamps:
            row = {
                'instance_id': instance_id,
                'instance_type': instance['instance_type'],
                'timestamp': timestamp,  # Use actual CloudWatch timestamp
                'cpu_utilization': metric_lookup['cpu_utilization'].get(timestamp),
                'memory_utilization': None,  # Not available in standard CloudWatch
                'network_in': metric_lookup['network_in'].get(timestamp),
                'network_out': metric_lookup['network_out'].get(timestamp),
            }
            all_metrics.append(row)
    
    if not all_metrics:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_metrics)
    return df


def get_memory_utilization_estimate(instance_type: str) -> Optional[float]:
    """
    Estimate memory utilization based on instance type specifications.
    This is a placeholder - in production, you'd use custom CloudWatch metrics
    or CloudWatch Insights queries.
    
    Args:
        instance_type: EC2 instance type (e.g., 'm5.large')
    
    Returns:
        Estimated memory utilization percentage (0-100)
    """
    # This is a placeholder - you'd need to implement actual memory monitoring
    # Options:
    # 1. Use CloudWatch custom metrics (requires CloudWatch agent)
    # 2. Use Systems Manager to run commands and collect metrics
    # 3. Use CloudWatch Insights queries
    # 4. Estimate based on instance type and workload patterns
    
    return None  # Return None to indicate we don't have real memory data


