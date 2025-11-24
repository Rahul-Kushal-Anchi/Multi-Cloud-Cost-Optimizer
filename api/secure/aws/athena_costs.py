import time
from typing import List, Dict
from botocore.config import Config
from fastapi import APIRouter, Depends, HTTPException

try:
    from api.auth_onboarding.routes import get_current_tenant
    from api.auth_onboarding.models import Tenant
    from api.secure.aws.assume_role import assume_vendor_role
except ImportError:
    # Fallback for Docker container
    from auth_onboarding.routes import get_current_tenant
    from auth_onboarding.models import Tenant
    from secure.aws.assume_role import assume_vendor_role

router = APIRouter(prefix="/api", tags=["costs-real"])

ATHENA_TIMEOUT = 60  # seconds


def run_athena_query(session, workgroup: str, database: str, query: str) -> List[Dict]:
    athena = session.client("athena", config=Config(retries={"max_attempts": 8}))
    start = athena.start_query_execution(QueryString=query, WorkGroup=workgroup)
    qid = start["QueryExecutionId"]
    t0 = time.time()
    while True:
        q = athena.get_query_execution(QueryExecutionId=qid)
        state = q["QueryExecution"]["Status"]["State"]
        if state == "SUCCEEDED":
            break
        if state in ("FAILED", "CANCELLED"):
            reason = (
                q.get("QueryExecution", {})
                .get("Status", {})
                .get("StateChangeReason", "")
            )
            raise RuntimeError(
                f"Athena query {qid} {state}: {reason or 'no reason returned'}"
            )
        if time.time() - t0 > ATHENA_TIMEOUT:
            raise TimeoutError("Athena query timed out")
        time.sleep(1.0)
    results, headers = [], None
    paginator = athena.get_paginator("get_query_results")
    for page in paginator.paginate(QueryExecutionId=qid):
        rows = page["ResultSet"]["Rows"]
        if headers is None:
            headers = [c["VarCharValue"] for c in rows[0]["Data"]]
            rows = rows[1:]
        for r in rows:
            rec = {}
            for i, cell in enumerate(r["Data"]):
                rec[headers[i]] = cell.get("VarCharValue")
            results.append(rec)
    return results


def cur_cost_query_sql(table: str, days: int = 7) -> str:
    return f"""
    SELECT
      product_product_name AS service,
      SUM(CAST(line_item_unblended_cost AS double)) AS cost
    FROM {table}
    WHERE line_item_usage_start_date >= date_add('day', -{days}, current_timestamp)
      AND "$path" LIKE '%.parquet'
    GROUP BY 1
    ORDER BY cost DESC
    LIMIT 50
    """


@router.get("/costs")
def get_costs(days: int = 7, tenant: Tenant = Depends(get_current_tenant)):
    """Get cost data for the authenticated tenant from Athena"""
    # Check if tenant has AWS connection configured
    if not (
        tenant.aws_role_arn
        and tenant.external_id
        and tenant.athena_db
        and tenant.athena_table
        and tenant.athena_results_bucket
    ):
        raise HTTPException(
            status_code=400,
            detail="Tenant is not connected. Please configure AWS connection first.",
        )

    try:
        # Assume role for tenant's AWS account
        session = assume_vendor_role(
            tenant.aws_role_arn, tenant.external_id, tenant.region or "us-east-1"
        )

        # Build Athena query for daily costs
        query = f"""
        SELECT 
          date_trunc('day', line_item_usage_start_date) AS day,
          SUM(COALESCE(CAST(line_item_unblended_cost AS double), 0)) AS cost
        FROM {tenant.athena_db}.{tenant.athena_table}
        WHERE line_item_usage_start_date >= date_add('day', -{days}, current_timestamp)
          AND "$path" LIKE '%.parquet'
        GROUP BY 1
        ORDER BY 1 ASC
        """

        # Execute query
        athena = session.client("athena", config=Config(retries={"max_attempts": 8}))
        # When using a workgroup with EnforceWorkGroupConfiguration=true,
        # don't pass ResultConfiguration - it will use the workgroup's configured output location
        query_params = {
            "QueryString": query,
            "QueryExecutionContext": {"Database": tenant.athena_db},
            "WorkGroup": tenant.athena_workgroup or "primary",
        }
        # Only add ResultConfiguration if workgroup doesn't enforce it
        # (Most workgroups do enforce, so we skip it by default)

        qid = athena.start_query_execution(**query_params)["QueryExecutionId"]

        # Wait for query to complete
        state = "RUNNING"
        timeout = time.time() + ATHENA_TIMEOUT
        while state in ("RUNNING", "QUEUED") and time.time() < timeout:
            time.sleep(1.2)
            state = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"][
                "Status"
            ]["State"]

        if state != "SUCCEEDED":
            error_msg = (
                athena.get_query_execution(QueryExecutionId=qid)
                .get("QueryExecution", {})
                .get("Status", {})
                .get("StateChangeReason", state)
            )
            raise HTTPException(
                status_code=500, detail=f"Athena query failed: {error_msg}"
            )

        # Get results
        rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
        data = []
        total = 0.0

        # Skip header row
        for r in rows[1:]:
            if len(r["Data"]) >= 2:
                day = r["Data"][0].get("VarCharValue", "")
                cost = float(r["Data"][1].get("VarCharValue", "0"))
                data.append({"date": day[:10] if day else "", "cost": round(cost, 2)})
                total += cost

        return {"period": f"{days}d", "data": data, "total": round(total, 2)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Athena: {str(e)}")
