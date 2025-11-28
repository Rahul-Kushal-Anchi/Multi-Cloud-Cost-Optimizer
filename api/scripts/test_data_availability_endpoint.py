#!/usr/bin/env python3
"""
Test script for the data availability endpoint.
This tests the endpoint logic directly without needing a running server.
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from sqlmodel import Session, select, create_engine
from api.auth_onboarding.models import Tenant
from api.secure.aws.assume_role import assume_vendor_role
from botocore.config import Config
import time

def test_data_availability_logic():
    """Test the data availability check logic"""
    print("🧪 Testing Data Availability Endpoint Logic\n")
    
    # Check database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set")
        print("   Set it with: export DATABASE_URL='postgresql+psycopg://...'")
        return False
    
    print(f"✅ Database URL: {db_url.split('@')[-1] if '@' in db_url else 'configured'}")
    
    # Create engine and session
    try:
        engine = create_engine(db_url)
        with Session(engine) as session:
            # Find a tenant with AWS connection
            tenant = session.exec(
                select(Tenant)
                .where(Tenant.aws_role_arn.isnot(None))
                .where(Tenant.athena_db.isnot(None))
                .where(Tenant.athena_table.isnot(None))
            ).first()
            
            if not tenant:
                print("\n⚠️  No tenant found with AWS connection configured")
                print("   Please connect an AWS account first via the UI")
                return False
            
            print(f"\n✅ Found tenant: {tenant.name} (ID: {tenant.id})")
            print(f"   AWS Role ARN: {tenant.aws_role_arn}")
            print(f"   Athena DB: {tenant.athena_db}")
            print(f"   Athena Table: {tenant.athena_table}")
            print(f"   Region: {tenant.region or 'us-east-1'}")
            
            # Test AWS connection
            print("\n🔐 Testing AWS connection...")
            try:
                aws_session = assume_vendor_role(
                    tenant.aws_role_arn,
                    tenant.external_id,
                    tenant.region or "us-east-1"
                )
                sts = aws_session.client('sts')
                identity = sts.get_caller_identity()
                print(f"   ✅ Connected to AWS Account: {identity.get('Account')}")
            except Exception as e:
                print(f"   ❌ AWS connection failed: {e}")
                return False
            
            # Query Athena for data availability
            print("\n📊 Querying Athena for data availability...")
            try:
                athena = aws_session.client("athena", config=Config(retries={"max_attempts": 8}))
                workgroup = tenant.athena_workgroup or "primary"
                database = tenant.athena_db
                table = f"{tenant.athena_db}.{tenant.athena_table}"
                
                query = f"""
                SELECT
                    MIN(line_item_usage_start_date) AS earliest_date,
                    MAX(line_item_usage_start_date) AS latest_date,
                    COUNT(DISTINCT date_trunc('day', line_item_usage_start_date)) AS unique_days,
                    COUNT(*) AS total_records
                FROM {table}
                WHERE "$path" LIKE '%.parquet'
                """
                
                query_params = {
                    "QueryString": query,
                    "QueryExecutionContext": {"Database": database},
                    "WorkGroup": workgroup,
                }
                
                print(f"   Executing query on {table}...")
                qid = athena.start_query_execution(**query_params)["QueryExecutionId"]
                print(f"   Query ID: {qid}")
                
                # Wait for query to complete
                state = "RUNNING"
                timeout = time.time() + 60
                while state in ("RUNNING", "QUEUED") and time.time() < timeout:
                    time.sleep(1.2)
                    state = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]["State"]
                    if state in ("RUNNING", "QUEUED"):
                        print(f"   Status: {state}...", end="\r")
                
                print()  # New line after status updates
                
                if state != "SUCCEEDED":
                    error_msg = (
                        athena.get_query_execution(QueryExecutionId=qid)
                        .get("QueryExecution", {})
                        .get("Status", {})
                        .get("StateChangeReason", state)
                    )
                    print(f"   ❌ Query failed: {error_msg}")
                    return False
                
                # Get results
                rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
                if len(rows) < 2:
                    print("   ❌ No results returned")
                    return False
                
                # Parse results
                headers = [c["VarCharValue"] for c in rows[0]["Data"]]
                data_row = rows[1]["Data"]
                result = dict(zip(headers, [cell.get("VarCharValue", "") for cell in data_row]))
                
                earliest_date_str = result.get('earliest_date') or result.get('EARLIEST_DATE')
                latest_date_str = result.get('latest_date') or result.get('LATEST_DATE')
                unique_days = int(result.get('unique_days') or result.get('UNIQUE_DAYS') or 0)
                total_records = int(result.get('total_records') or result.get('TOTAL_RECORDS') or 0)
                
                if not earliest_date_str or not latest_date_str:
                    print("   ❌ Could not determine date range")
                    return False
                
                # Parse dates
                earliest = datetime.strptime(earliest_date_str[:10], '%Y-%m-%d')
                latest = datetime.strptime(latest_date_str[:10], '%Y-%m-%d')
                days_available = (latest - earliest).days + 1
                days_from_today = (datetime.utcnow() - latest).days if latest < datetime.utcnow() else 0
                
                # Determine recommendation
                sufficient = days_available >= 90
                recommendation = "train_90_days" if days_available >= 90 else "wait_for_more_data"
                if days_available >= 180:
                    recommendation = "train_180_days"
                elif days_available >= 120:
                    recommendation = "train_120_days"
                
                # Display results
                print("\n" + "="*60)
                print("📊 DATA AVAILABILITY RESULTS")
                print("="*60)
                print(f"Earliest Date:     {earliest_date_str[:10]}")
                print(f"Latest Date:       {latest_date_str[:10]}")
                print(f"Days Available:    {days_available}")
                print(f"Unique Days:        {unique_days}")
                print(f"Total Records:      {total_records:,}")
                print(f"Days From Today:    {days_from_today}")
                print(f"\nSufficient for ML: {'✅ YES' if sufficient else '⚠️  NO'}")
                print(f"Recommendation:     {recommendation}")
                
                if sufficient:
                    print(f"\n✅ You have {days_available} days of data. Sufficient for anomaly detection!")
                else:
                    print(f"\n⚠️  You have {days_available} days of data. Need {90 - days_available} more days.")
                
                print("="*60)
                return True
                
            except Exception as e:
                print(f"   ❌ Athena query failed: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_availability_logic()
    sys.exit(0 if success else 1)


Test script for the data availability endpoint.
This tests the endpoint logic directly without needing a running server.
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from sqlmodel import Session, select, create_engine
from api.auth_onboarding.models import Tenant
from api.secure.aws.assume_role import assume_vendor_role
from botocore.config import Config
import time

def test_data_availability_logic():
    """Test the data availability check logic"""
    print("🧪 Testing Data Availability Endpoint Logic\n")
    
    # Check database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set")
        print("   Set it with: export DATABASE_URL='postgresql+psycopg://...'")
        return False
    
    print(f"✅ Database URL: {db_url.split('@')[-1] if '@' in db_url else 'configured'}")
    
    # Create engine and session
    try:
        engine = create_engine(db_url)
        with Session(engine) as session:
            # Find a tenant with AWS connection
            tenant = session.exec(
                select(Tenant)
                .where(Tenant.aws_role_arn.isnot(None))
                .where(Tenant.athena_db.isnot(None))
                .where(Tenant.athena_table.isnot(None))
            ).first()
            
            if not tenant:
                print("\n⚠️  No tenant found with AWS connection configured")
                print("   Please connect an AWS account first via the UI")
                return False
            
            print(f"\n✅ Found tenant: {tenant.name} (ID: {tenant.id})")
            print(f"   AWS Role ARN: {tenant.aws_role_arn}")
            print(f"   Athena DB: {tenant.athena_db}")
            print(f"   Athena Table: {tenant.athena_table}")
            print(f"   Region: {tenant.region or 'us-east-1'}")
            
            # Test AWS connection
            print("\n🔐 Testing AWS connection...")
            try:
                aws_session = assume_vendor_role(
                    tenant.aws_role_arn,
                    tenant.external_id,
                    tenant.region or "us-east-1"
                )
                sts = aws_session.client('sts')
                identity = sts.get_caller_identity()
                print(f"   ✅ Connected to AWS Account: {identity.get('Account')}")
            except Exception as e:
                print(f"   ❌ AWS connection failed: {e}")
                return False
            
            # Query Athena for data availability
            print("\n📊 Querying Athena for data availability...")
            try:
                athena = aws_session.client("athena", config=Config(retries={"max_attempts": 8}))
                workgroup = tenant.athena_workgroup or "primary"
                database = tenant.athena_db
                table = f"{tenant.athena_db}.{tenant.athena_table}"
                
                query = f"""
                SELECT
                    MIN(line_item_usage_start_date) AS earliest_date,
                    MAX(line_item_usage_start_date) AS latest_date,
                    COUNT(DISTINCT date_trunc('day', line_item_usage_start_date)) AS unique_days,
                    COUNT(*) AS total_records
                FROM {table}
                WHERE "$path" LIKE '%.parquet'
                """
                
                query_params = {
                    "QueryString": query,
                    "QueryExecutionContext": {"Database": database},
                    "WorkGroup": workgroup,
                }
                
                print(f"   Executing query on {table}...")
                qid = athena.start_query_execution(**query_params)["QueryExecutionId"]
                print(f"   Query ID: {qid}")
                
                # Wait for query to complete
                state = "RUNNING"
                timeout = time.time() + 60
                while state in ("RUNNING", "QUEUED") and time.time() < timeout:
                    time.sleep(1.2)
                    state = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]["State"]
                    if state in ("RUNNING", "QUEUED"):
                        print(f"   Status: {state}...", end="\r")
                
                print()  # New line after status updates
                
                if state != "SUCCEEDED":
                    error_msg = (
                        athena.get_query_execution(QueryExecutionId=qid)
                        .get("QueryExecution", {})
                        .get("Status", {})
                        .get("StateChangeReason", state)
                    )
                    print(f"   ❌ Query failed: {error_msg}")
                    return False
                
                # Get results
                rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
                if len(rows) < 2:
                    print("   ❌ No results returned")
                    return False
                
                # Parse results
                headers = [c["VarCharValue"] for c in rows[0]["Data"]]
                data_row = rows[1]["Data"]
                result = dict(zip(headers, [cell.get("VarCharValue", "") for cell in data_row]))
                
                earliest_date_str = result.get('earliest_date') or result.get('EARLIEST_DATE')
                latest_date_str = result.get('latest_date') or result.get('LATEST_DATE')
                unique_days = int(result.get('unique_days') or result.get('UNIQUE_DAYS') or 0)
                total_records = int(result.get('total_records') or result.get('TOTAL_RECORDS') or 0)
                
                if not earliest_date_str or not latest_date_str:
                    print("   ❌ Could not determine date range")
                    return False
                
                # Parse dates
                earliest = datetime.strptime(earliest_date_str[:10], '%Y-%m-%d')
                latest = datetime.strptime(latest_date_str[:10], '%Y-%m-%d')
                days_available = (latest - earliest).days + 1
                days_from_today = (datetime.utcnow() - latest).days if latest < datetime.utcnow() else 0
                
                # Determine recommendation
                sufficient = days_available >= 90
                recommendation = "train_90_days" if days_available >= 90 else "wait_for_more_data"
                if days_available >= 180:
                    recommendation = "train_180_days"
                elif days_available >= 120:
                    recommendation = "train_120_days"
                
                # Display results
                print("\n" + "="*60)
                print("📊 DATA AVAILABILITY RESULTS")
                print("="*60)
                print(f"Earliest Date:     {earliest_date_str[:10]}")
                print(f"Latest Date:       {latest_date_str[:10]}")
                print(f"Days Available:    {days_available}")
                print(f"Unique Days:        {unique_days}")
                print(f"Total Records:      {total_records:,}")
                print(f"Days From Today:    {days_from_today}")
                print(f"\nSufficient for ML: {'✅ YES' if sufficient else '⚠️  NO'}")
                print(f"Recommendation:     {recommendation}")
                
                if sufficient:
                    print(f"\n✅ You have {days_available} days of data. Sufficient for anomaly detection!")
                else:
                    print(f"\n⚠️  You have {days_available} days of data. Need {90 - days_available} more days.")
                
                print("="*60)
                return True
                
            except Exception as e:
                print(f"   ❌ Athena query failed: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_availability_logic()
    sys.exit(0 if success else 1)

