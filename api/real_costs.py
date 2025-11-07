"""
Real AWS Cost Data Integration via Cost Explorer API
"""
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal


class CostExplorerClient:
    """Client for fetching real AWS cost data via Cost Explorer API"""
    
    def __init__(self, region: str = "us-east-1"):
        self.ce = boto3.client('ce', region_name=region)
    
    def get_service_costs(self, days: int = 7) -> Dict[str, float]:
        """
        Get costs grouped by service for the last N days
        
        Returns:
            Dict mapping service names to total costs
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )
        
        service_costs = {}
        for result in response.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                service = group['Keys'][0]
                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                service_costs[service] = service_costs.get(service, 0) + amount
        
        return service_costs
    
    def get_cost_trends(self, days: int = 7) -> List[Dict]:
        """
        Get daily cost trends for the last N days
        
        Returns:
            List of dicts with 'date' and 'cost' keys
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
        
        trends = []
        for result in response.get('ResultsByTime', []):
            cost = float(result['Total']['UnblendedCost']['Amount'])
            date_str = result['TimePeriod']['Start']
            trends.append({
                'date': date_str,
                'cost': round(cost, 2),
                'trend': 'up' if cost > 0 else 'down'
            })
        
        return trends
    
    def get_total_cost(self, days: int = 7) -> float:
        """
        Get total cost for the last N days
        
        Returns:
            Total cost as float
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
        
        total = 0.0
        for result in response.get('ResultsByTime', []):
            total += float(result['Total']['UnblendedCost']['Amount'])
        
        return round(total, 2)


# Global client instance
_cost_client = None


def get_cost_client() -> CostExplorerClient:
    """Get or create Cost Explorer client singleton"""
    global _cost_client
    if _cost_client is None:
        _cost_client = CostExplorerClient()
    return _cost_client


