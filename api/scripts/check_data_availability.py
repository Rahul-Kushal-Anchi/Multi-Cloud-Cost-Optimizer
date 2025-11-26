#!/usr/bin/env python3
"""
Check Data Availability
Check how many days of REAL cost data are available in AWS CUR via Athena
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from api.secure.aws.assume_role import assume_vendor_role
import time
from botocore.config import Config
from api.auth_onboarding.routes import engine
from api.auth_onboarding.models import Tenant
from sqlmodel import Session, select
from datetime import datetime, timedelta

def check_data_availability():
    """Check how many days of cost data are available"""
    print("🔍 Checking Data Availability")
    print("=" * 60)
    
    with Session(engine) as session:
        # Find connected tenant
        tenant = session.exec(
            select(Tenant)
            .where(Tenant.aws_role_arn.isnot(None))
            .where(Tenant.athena_db.isnot(None))
            .where(Tenant.athena_table.isnot(None))
        ).first()
        
        if not tenant:
            print("❌ No tenant found with AWS connection configured")
            return False
        
        print(f"✅ Found tenant: {tenant.name}")
        print(f"   Athena DB: {tenant.athena_db}")
        print(f"   Athena Table: {tenant.athena_table}")
        print(f"   Region: {tenant.region}")
        
        try:
            # Get AWS session
            session_aws = assume_vendor_role(
                tenant.aws_role_arn,
                tenant.external_id,
                tenant.region or "us-east-1"
            )
            print(f"\n✅ AWS session created successfully")
            
            # Query to check date range of available data
            print("\n📊 Querying Athena for data availability...")
            
            table = f"{tenant.athena_db}.{tenant.athena_table}"
            query = f"""
            SELECT
              MIN(date(line_item_usage_start_date)) AS earliest_date,
              MAX(date(line_item_usage_start_date)) AS latest_date,
              COUNT(DISTINCT date(line_item_usage_start_date)) AS unique_days,
              COUNT(*) AS total_records
            FROM {table}
            WHERE "$path" LIKE '%.parquet'
            """
            
            print("   Running query...")
            
            # Execute Athena query
            athena = session_aws.client("athena", config=Config(retries={"max_attempts": 8}))
            query_params = {
                "QueryString": query,
                "QueryExecutionContext": {"Database": tenant.athena_db},
                "WorkGroup": tenant.athena_workgroup or "primary",
            }
            
            qid = athena.start_query_execution(**query_params)["QueryExecutionId"]
            
            # Wait for query to complete
            state = "RUNNING"
            timeout = time.time() + 60  # 60 second timeout
            while state in ("RUNNING", "QUEUED") and time.time() < timeout:
                time.sleep(1.2)
                state = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]["State"]
            
            if state != "SUCCEEDED":
                error_msg = (
                    athena.get_query_execution(QueryExecutionId=qid)
                    .get("QueryExecution", {})
                    .get("Status", {})
                    .get("StateChangeReason", state)
                )
                raise Exception(f"Athena query failed: {error_msg}")
            
            # Get results
            rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
            if len(rows) < 2:
                raise Exception("No results returned")
            
            # Parse results
            headers = [c["VarCharValue"] for c in rows[0]["Data"]]
            data_row = rows[1]["Data"]
            results = [dict(zip(headers, [cell.get("VarCharValue", "") for cell in data_row]))]
            
            if not results or len(results) == 0:
                print("⚠️  No data found in Athena")
                return False
            
            result = results[0]
            earliest_date = result.get('earliest_date') or result.get('EARLIEST_DATE')
            latest_date = result.get('latest_date') or result.get('LATEST_DATE')
            unique_days = result.get('unique_days') or result.get('UNIQUE_DAYS')
            total_records = result.get('total_records') or result.get('TOTAL_RECORDS')
            
            if not earliest_date or not latest_date:
                print("⚠️  Could not determine date range")
                return False
            
            # Parse dates
            try:
                earliest = datetime.strptime(earliest_date[:10], '%Y-%m-%d')
                latest = datetime.strptime(latest_date[:10], '%Y-%m-%d')
                days_available = (latest - earliest).days + 1
            except Exception as e:
                print(f"⚠️  Error parsing dates: {e}")
                return False
            
            print(f"\n✅ Data Availability Results:")
            print(f"   📅 Earliest Date: {earliest_date[:10]}")
            print(f"   📅 Latest Date: {latest_date[:10]}")
            print(f"   📊 Total Days Available: {days_available} days")
            print(f"   📊 Unique Days: {unique_days}")
            print(f"   📊 Total Records: {total_records:,}")
            
            # Calculate days from today
            today = datetime.utcnow()
            days_from_today = (today - latest).days if latest < today else 0
            
            print(f"\n📈 Analysis:")
            print(f"   Latest data is {days_from_today} days old")
            
            if days_available >= 90:
                print(f"\n✅ SUFFICIENT DATA FOR ANOMALY DETECTION!")
                print(f"   ✅ You have {days_available} days of data")
                print(f"   ✅ More than the 90 days required")
                print(f"   ✅ Can train model on last 90 days")
                
                if days_available >= 180:
                    print(f"\n🎉 EXCELLENT! You have {days_available} days")
                    print(f"   💡 Can train on 180 days for better accuracy")
                elif days_available >= 120:
                    print(f"\n💡 GOOD! You have {days_available} days")
                    print(f"   💡 Can train on 120 days for better accuracy")
            else:
                print(f"\n⚠️  LIMITED DATA")
                print(f"   ⚠️  Only {days_available} days available")
                print(f"   ⚠️  Need at least 90 days for good results")
                print(f"   💡 Wait for more CUR data to accumulate")
            
            # Check data quality (recent data)
            print(f"\n📋 Data Quality Check:")
            if days_from_today <= 2:
                print(f"   ✅ Data is fresh (less than 2 days old)")
            elif days_from_today <= 7:
                print(f"   ⚠️  Data is {days_from_today} days old (CUR updates daily)")
            else:
                print(f"   ⚠️  Data is {days_from_today} days old (may need to check CUR)")
            
            # Recommendation
            print(f"\n💡 Recommendation:")
            if days_available >= 90:
                print(f"   ✅ Train model on last 90 days")
                if days_available >= 180:
                    print(f"   ✅ Or train on last 180 days for better accuracy")
                print(f"   ✅ Model will work well with this data")
            else:
                print(f"   ⚠️  Wait until you have 90+ days of data")
                print(f"   ⚠️  Current: {days_available} days")
                print(f"   ⚠️  Need: {90 - days_available} more days")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🔍 Checking AWS CUR Data Availability")
    print("=" * 60)
    print()
    
    success = check_data_availability()
    
    if success:
        print("\n✅ Data availability check completed!")
    else:
        print("\n❌ Data availability check failed")
        sys.exit(1)

