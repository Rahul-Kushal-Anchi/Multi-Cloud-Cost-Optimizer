#!/usr/bin/env python3
"""
Check AWS Data Directly
Directly queries your AWS account via Athena to check data availability
"""

import sys
import os
import time
from datetime import datetime
from botocore.config import Config

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlmodel import SQLModel, create_engine, Session, select
from api.auth_onboarding.models import Tenant
from api.secure.aws.assume_role import assume_vendor_role

def check_aws_data():
    """Check AWS data availability directly"""
    print("🔍 Checking Your AWS Account Data")
    print("=" * 60)
    
    # Try to get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./saas.db")
    
    # If DATABASE_URL points to production, use that
    # Otherwise try common production database URLs
    if "sqlite" in database_url.lower():
        print("⚠️  Using local SQLite database")
        print("   If your app uses PostgreSQL, set DATABASE_URL environment variable")
        print("   Example: export DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
        print()
    
    engine = create_engine(database_url, echo=False)
    
    with Session(engine) as session:
        # Find connected tenant
        print("📋 Looking for connected tenant...")
        tenant = session.exec(
            select(Tenant)
            .where(Tenant.aws_role_arn.isnot(None))
            .where(Tenant.athena_db.isnot(None))
            .where(Tenant.athena_table.isnot(None))
        ).first()
        
        if not tenant:
            print("❌ No tenant found with AWS connection configured")
            print("\n💡 Make sure:")
            print("   1. Your app database is accessible")
            print("   2. DATABASE_URL environment variable is set correctly")
            print("   3. Tenant has AWS connection configured")
            return False
        
        print(f"✅ Found tenant: {tenant.name}")
        print(f"   Tenant ID: {tenant.id}")
        print(f"   AWS Role ARN: {tenant.aws_role_arn[:50]}...")
        print(f"   Athena DB: {tenant.athena_db}")
        print(f"   Athena Table: {tenant.athena_table}")
        print(f"   Region: {tenant.region}")
        
        try:
            print(f"\n🔐 Connecting to AWS account...")
            # Get AWS session using tenant's credentials
            aws_session = assume_vendor_role(
                tenant.aws_role_arn,
                tenant.external_id,
                tenant.region or "us-east-1"
            )
            print(f"✅ Successfully connected to AWS account")
            
            # Query to check date range of available data
            print(f"\n📊 Querying Athena for cost data availability...")
            
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
            
            print("   Executing Athena query...")
            
            # Execute Athena query
            athena = aws_session.client("athena", config=Config(retries={"max_attempts": 8}))
            query_params = {
                "QueryString": query,
                "QueryExecutionContext": {"Database": tenant.athena_db},
                "WorkGroup": tenant.athena_workgroup or "primary",
            }
            
            qid = athena.start_query_execution(**query_params)["QueryExecutionId"]
            print(f"   Query ID: {qid}")
            print("   Waiting for query to complete...")
            
            # Wait for query to complete
            state = "RUNNING"
            timeout = time.time() + 60  # 60 second timeout
            while state in ("RUNNING", "QUEUED") and time.time() < timeout:
                time.sleep(1.2)
                exec_result = athena.get_query_execution(QueryExecutionId=qid)
                state = exec_result["QueryExecution"]["Status"]["State"]
                if state == "RUNNING":
                    print("   ⏳ Still running...")
            
            if state != "SUCCEEDED":
                error_msg = (
                    exec_result.get("QueryExecution", {})
                    .get("Status", {})
                    .get("StateChangeReason", state)
                )
                raise Exception(f"Athena query failed ({state}): {error_msg}")
            
            print("   ✅ Query completed successfully!")
            
            # Get results
            print("   Fetching results...")
            rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
            if len(rows) < 2:
                raise Exception("No results returned")
            
            # Parse results
            headers = [c["VarCharValue"] for c in rows[0]["Data"]]
            data_row = rows[1]["Data"]
            result = dict(zip(headers, [cell.get("VarCharValue", "") for cell in data_row]))
            
            earliest_date = result.get('earliest_date') or result.get('EARLIEST_DATE')
            latest_date = result.get('latest_date') or result.get('LATEST_DATE')
            unique_days = int(result.get('unique_days') or result.get('UNIQUE_DAYS') or 0)
            total_records = int(result.get('total_records') or result.get('TOTAL_RECORDS') or 0)
            
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
            
            # Calculate days from today
            today = datetime.utcnow()
            days_from_today = (today - latest).days if latest < today else 0
            
            print(f"\n" + "=" * 60)
            print(f"📊 DATA AVAILABILITY RESULTS")
            print(f"=" * 60)
            print(f"   📅 Earliest Date: {earliest_date[:10]}")
            print(f"   📅 Latest Date: {latest_date[:10]}")
            print(f"   📊 Total Days Available: {days_available} days")
            print(f"   📊 Unique Days: {unique_days}")
            print(f"   📊 Total Records: {total_records:,}")
            print(f"   📊 Data Age: {days_from_today} days old")
            
            print(f"\n" + "=" * 60)
            print(f"🎯 ANOMALY DETECTION ASSESSMENT")
            print(f"=" * 60)
            
            if days_available >= 90:
                print(f"\n✅ SUFFICIENT DATA FOR ANOMALY DETECTION!")
                print(f"   ✅ You have {days_available} days of REAL cost data")
                print(f"   ✅ More than the 90 days required")
                print(f"   ✅ Ready to train ML model")
                
                if days_available >= 180:
                    print(f"\n🎉 EXCELLENT! You have {days_available} days")
                    print(f"   💡 Recommendation: Train on last 180 days for best accuracy")
                    print(f"   💡 This will capture seasonal patterns and trends")
                elif days_available >= 120:
                    print(f"\n💡 GREAT! You have {days_available} days")
                    print(f"   💡 Recommendation: Train on last 120 days for better accuracy")
                else:
                    print(f"\n💡 Recommendation: Train on last 90 days")
                    print(f"   💡 Model will work well with this data")
            else:
                print(f"\n⚠️  INSUFFICIENT DATA")
                print(f"   ⚠️  Only {days_available} days available")
                print(f"   ⚠️  Need at least 90 days for good results")
                print(f"   ⚠️  Need {90 - days_available} more days")
                print(f"\n💡 What to do:")
                print(f"   1. Wait for more CUR data to accumulate")
                print(f"   2. Check if CUR is generating reports daily")
                print(f"   3. Verify Athena table has data")
            
            # Data quality check
            print(f"\n" + "=" * 60)
            print(f"📋 DATA QUALITY CHECK")
            print(f"=" * 60)
            
            if days_from_today <= 2:
                print(f"   ✅ Data is fresh (less than 2 days old)")
                print(f"   ✅ CUR is updating regularly")
            elif days_from_today <= 7:
                print(f"   ⚠️  Data is {days_from_today} days old")
                print(f"   ⚠️  CUR should update daily - check if reports are generating")
            else:
                print(f"   ⚠️  Data is {days_from_today} days old")
                print(f"   ⚠️  May need to check CUR configuration")
            
            if total_records > 0:
                avg_records_per_day = total_records / unique_days if unique_days > 0 else 0
                print(f"   📊 Average records per day: {avg_records_per_day:,.0f}")
                if avg_records_per_day > 100:
                    print(f"   ✅ Good data density")
                elif avg_records_per_day > 10:
                    print(f"   ⚠️  Moderate data density")
                else:
                    print(f"   ⚠️  Low data density - may indicate limited AWS usage")
            
            print(f"\n" + "=" * 60)
            print(f"🚀 NEXT STEPS")
            print(f"=" * 60)
            
            if days_available >= 90:
                print(f"   ✅ Proceed with anomaly detection implementation")
                print(f"   ✅ Train model on last {min(days_available, 180)} days")
                print(f"   ✅ Start detecting anomalies immediately")
            else:
                print(f"   ⏳ Wait for {90 - days_available} more days of data")
                print(f"   ⏳ Then proceed with anomaly detection")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print(f"\n💡 Troubleshooting:")
            print(f"   1. Check AWS credentials are correct")
            print(f"   2. Verify Athena database/table names")
            print(f"   3. Ensure CUR is generating data")
            print(f"   4. Check IAM permissions for Athena queries")
            return False

if __name__ == "__main__":
    print("🔍 Checking Your AWS Account Data Availability")
    print("=" * 60)
    print()
    
    success = check_aws_data()
    
    if success:
        print("\n✅ Data check completed successfully!")
    else:
        print("\n❌ Data check failed")
        print("\n💡 Alternative: Use the API endpoint:")
        print("   GET /api/ml/data-availability")
        sys.exit(1)


"""
Check AWS Data Directly
Directly queries your AWS account via Athena to check data availability
"""

import sys
import os
import time
from datetime import datetime
from botocore.config import Config

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlmodel import SQLModel, create_engine, Session, select
from api.auth_onboarding.models import Tenant
from api.secure.aws.assume_role import assume_vendor_role

def check_aws_data():
    """Check AWS data availability directly"""
    print("🔍 Checking Your AWS Account Data")
    print("=" * 60)
    
    # Try to get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./saas.db")
    
    # If DATABASE_URL points to production, use that
    # Otherwise try common production database URLs
    if "sqlite" in database_url.lower():
        print("⚠️  Using local SQLite database")
        print("   If your app uses PostgreSQL, set DATABASE_URL environment variable")
        print("   Example: export DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
        print()
    
    engine = create_engine(database_url, echo=False)
    
    with Session(engine) as session:
        # Find connected tenant
        print("📋 Looking for connected tenant...")
        tenant = session.exec(
            select(Tenant)
            .where(Tenant.aws_role_arn.isnot(None))
            .where(Tenant.athena_db.isnot(None))
            .where(Tenant.athena_table.isnot(None))
        ).first()
        
        if not tenant:
            print("❌ No tenant found with AWS connection configured")
            print("\n💡 Make sure:")
            print("   1. Your app database is accessible")
            print("   2. DATABASE_URL environment variable is set correctly")
            print("   3. Tenant has AWS connection configured")
            return False
        
        print(f"✅ Found tenant: {tenant.name}")
        print(f"   Tenant ID: {tenant.id}")
        print(f"   AWS Role ARN: {tenant.aws_role_arn[:50]}...")
        print(f"   Athena DB: {tenant.athena_db}")
        print(f"   Athena Table: {tenant.athena_table}")
        print(f"   Region: {tenant.region}")
        
        try:
            print(f"\n🔐 Connecting to AWS account...")
            # Get AWS session using tenant's credentials
            aws_session = assume_vendor_role(
                tenant.aws_role_arn,
                tenant.external_id,
                tenant.region or "us-east-1"
            )
            print(f"✅ Successfully connected to AWS account")
            
            # Query to check date range of available data
            print(f"\n📊 Querying Athena for cost data availability...")
            
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
            
            print("   Executing Athena query...")
            
            # Execute Athena query
            athena = aws_session.client("athena", config=Config(retries={"max_attempts": 8}))
            query_params = {
                "QueryString": query,
                "QueryExecutionContext": {"Database": tenant.athena_db},
                "WorkGroup": tenant.athena_workgroup or "primary",
            }
            
            qid = athena.start_query_execution(**query_params)["QueryExecutionId"]
            print(f"   Query ID: {qid}")
            print("   Waiting for query to complete...")
            
            # Wait for query to complete
            state = "RUNNING"
            timeout = time.time() + 60  # 60 second timeout
            while state in ("RUNNING", "QUEUED") and time.time() < timeout:
                time.sleep(1.2)
                exec_result = athena.get_query_execution(QueryExecutionId=qid)
                state = exec_result["QueryExecution"]["Status"]["State"]
                if state == "RUNNING":
                    print("   ⏳ Still running...")
            
            if state != "SUCCEEDED":
                error_msg = (
                    exec_result.get("QueryExecution", {})
                    .get("Status", {})
                    .get("StateChangeReason", state)
                )
                raise Exception(f"Athena query failed ({state}): {error_msg}")
            
            print("   ✅ Query completed successfully!")
            
            # Get results
            print("   Fetching results...")
            rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
            if len(rows) < 2:
                raise Exception("No results returned")
            
            # Parse results
            headers = [c["VarCharValue"] for c in rows[0]["Data"]]
            data_row = rows[1]["Data"]
            result = dict(zip(headers, [cell.get("VarCharValue", "") for cell in data_row]))
            
            earliest_date = result.get('earliest_date') or result.get('EARLIEST_DATE')
            latest_date = result.get('latest_date') or result.get('LATEST_DATE')
            unique_days = int(result.get('unique_days') or result.get('UNIQUE_DAYS') or 0)
            total_records = int(result.get('total_records') or result.get('TOTAL_RECORDS') or 0)
            
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
            
            # Calculate days from today
            today = datetime.utcnow()
            days_from_today = (today - latest).days if latest < today else 0
            
            print(f"\n" + "=" * 60)
            print(f"📊 DATA AVAILABILITY RESULTS")
            print(f"=" * 60)
            print(f"   📅 Earliest Date: {earliest_date[:10]}")
            print(f"   📅 Latest Date: {latest_date[:10]}")
            print(f"   📊 Total Days Available: {days_available} days")
            print(f"   📊 Unique Days: {unique_days}")
            print(f"   📊 Total Records: {total_records:,}")
            print(f"   📊 Data Age: {days_from_today} days old")
            
            print(f"\n" + "=" * 60)
            print(f"🎯 ANOMALY DETECTION ASSESSMENT")
            print(f"=" * 60)
            
            if days_available >= 90:
                print(f"\n✅ SUFFICIENT DATA FOR ANOMALY DETECTION!")
                print(f"   ✅ You have {days_available} days of REAL cost data")
                print(f"   ✅ More than the 90 days required")
                print(f"   ✅ Ready to train ML model")
                
                if days_available >= 180:
                    print(f"\n🎉 EXCELLENT! You have {days_available} days")
                    print(f"   💡 Recommendation: Train on last 180 days for best accuracy")
                    print(f"   💡 This will capture seasonal patterns and trends")
                elif days_available >= 120:
                    print(f"\n💡 GREAT! You have {days_available} days")
                    print(f"   💡 Recommendation: Train on last 120 days for better accuracy")
                else:
                    print(f"\n💡 Recommendation: Train on last 90 days")
                    print(f"   💡 Model will work well with this data")
            else:
                print(f"\n⚠️  INSUFFICIENT DATA")
                print(f"   ⚠️  Only {days_available} days available")
                print(f"   ⚠️  Need at least 90 days for good results")
                print(f"   ⚠️  Need {90 - days_available} more days")
                print(f"\n💡 What to do:")
                print(f"   1. Wait for more CUR data to accumulate")
                print(f"   2. Check if CUR is generating reports daily")
                print(f"   3. Verify Athena table has data")
            
            # Data quality check
            print(f"\n" + "=" * 60)
            print(f"📋 DATA QUALITY CHECK")
            print(f"=" * 60)
            
            if days_from_today <= 2:
                print(f"   ✅ Data is fresh (less than 2 days old)")
                print(f"   ✅ CUR is updating regularly")
            elif days_from_today <= 7:
                print(f"   ⚠️  Data is {days_from_today} days old")
                print(f"   ⚠️  CUR should update daily - check if reports are generating")
            else:
                print(f"   ⚠️  Data is {days_from_today} days old")
                print(f"   ⚠️  May need to check CUR configuration")
            
            if total_records > 0:
                avg_records_per_day = total_records / unique_days if unique_days > 0 else 0
                print(f"   📊 Average records per day: {avg_records_per_day:,.0f}")
                if avg_records_per_day > 100:
                    print(f"   ✅ Good data density")
                elif avg_records_per_day > 10:
                    print(f"   ⚠️  Moderate data density")
                else:
                    print(f"   ⚠️  Low data density - may indicate limited AWS usage")
            
            print(f"\n" + "=" * 60)
            print(f"🚀 NEXT STEPS")
            print(f"=" * 60)
            
            if days_available >= 90:
                print(f"   ✅ Proceed with anomaly detection implementation")
                print(f"   ✅ Train model on last {min(days_available, 180)} days")
                print(f"   ✅ Start detecting anomalies immediately")
            else:
                print(f"   ⏳ Wait for {90 - days_available} more days of data")
                print(f"   ⏳ Then proceed with anomaly detection")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print(f"\n💡 Troubleshooting:")
            print(f"   1. Check AWS credentials are correct")
            print(f"   2. Verify Athena database/table names")
            print(f"   3. Ensure CUR is generating data")
            print(f"   4. Check IAM permissions for Athena queries")
            return False

if __name__ == "__main__":
    print("🔍 Checking Your AWS Account Data Availability")
    print("=" * 60)
    print()
    
    success = check_aws_data()
    
    if success:
        print("\n✅ Data check completed successfully!")
    else:
        print("\n❌ Data check failed")
        print("\n💡 Alternative: Use the API endpoint:")
        print("   GET /api/ml/data-availability")
        sys.exit(1)



