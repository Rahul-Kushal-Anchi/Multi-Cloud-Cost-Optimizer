#!/usr/bin/env python3
"""
Fix Cost Explorer API issues
"""

import boto3
from datetime import datetime, timedelta

def test_cost_explorer_fix():
    """Test Cost Explorer API with recent dates"""
    print("✅ Testing Cost Explorer API with recent dates...")
    try:
        ce = boto3.client('ce')
        
        # Use recent dates (last 7 days)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='DAILY',
            Metrics=['BlendedCost']
        )
        
        print(f"✅ Cost Explorer API working with recent dates: {start_date} to {end_date}")
        print(f"✅ Retrieved {len(response['ResultsByTime'])} days of cost data")
        
        # Show sample data
        if response['ResultsByTime']:
            sample = response['ResultsByTime'][0]
            print(f"✅ Sample cost data: {sample['TimePeriod']['Start']} - ${sample['Total']['BlendedCost']['Amount']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cost Explorer still failing: {e}")
        return False

if __name__ == "__main__":
    test_cost_explorer_fix()
