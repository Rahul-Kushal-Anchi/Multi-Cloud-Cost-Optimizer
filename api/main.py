from fastapi import FastAPI, Depends, HTTPException, Header, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from statistics import mean
from uuid import uuid4
from sqlmodel import Session, select
import logging
import sys
import os

# Secure deps for real CUR
# Add parent directory to path to allow imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from api.secure.deps import get_tenant_session_and_meta
    from api.secure.aws.athena_costs import run_athena_query, cur_cost_query_sql

    CUR_AVAILABLE = True
except ImportError:
    try:
        # Try direct import for Docker container
        from secure.deps import get_tenant_session_and_meta
        from secure.aws.athena_costs import run_athena_query, cur_cost_query_sql

        CUR_AVAILABLE = True
    except Exception as e:
        # Log import errors for debugging deployment issues
        print(f"Warning: CUR modules not available: {e}")
        CUR_AVAILABLE = False
except Exception as e:
    print(f"Warning: CUR modules not available: {e}")
    CUR_AVAILABLE = False

try:
    from api.auth_onboarding.models import (
        Tenant,
        UserSettings,
        User,
        default_notifications,
        default_alerts,
        default_preferences,
    )
    # Import ML models for database initialization
    from api.ml.models import MLModel, Anomaly, Recommendation, Forecast, InstanceMetrics
    from api.auth_onboarding.routes import get_session
    from api.auth_onboarding.current import get_current_ctx
    from api.auth_onboarding.security import hash_password, verify_password
except ImportError:
    from auth_onboarding.models import (
        Tenant,
        UserSettings,
        User,
        default_notifications,
        default_alerts,
        default_preferences,
    )
    from auth_onboarding.routes import get_session
    from auth_onboarding.current import get_current_ctx
    from auth_onboarding.security import hash_password, verify_password

try:
    from api.secure.aws.assume_role import assume_vendor_role
    from api.services.aws_cost_service import aws_cost_service
except ImportError:
    from secure.aws.assume_role import assume_vendor_role
    from services.aws_cost_service import aws_cost_service

try:
    from api.real_costs import get_cost_client

    COST_EXPLORER_AVAILABLE = True
except ImportError:
    try:
        # Try direct import for Docker container
        from real_costs import get_cost_client

        COST_EXPLORER_AVAILABLE = True
    except Exception as e:
        print(f"Warning: Cost Explorer modules not available: {e}")
        COST_EXPLORER_AVAILABLE = False
except Exception as e:
    print(f"Warning: Cost Explorer modules not available: {e}")
    COST_EXPLORER_AVAILABLE = False

app = FastAPI(
    title="Cost Optimizer API", docs_url="/api/docs", openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("api.cost_optimizer")
logger.setLevel(logging.INFO)

# Include auth and onboarding routes
try:
    from api.auth_onboarding.routes import router as auth_router, init_db
    from api.auth_onboarding.admin import router as admin_router
    from api.auth_onboarding.owner_bootstrap import router as owner_bootstrap_router
    from api.auth_onboarding.invite import router as invite_router

    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(owner_bootstrap_router)
    app.include_router(invite_router)

    # Initialize database on startup
    @app.on_event("startup")
    def startup_db():
        try:
            init_db()
        except Exception as e:
            print(f"Warning: Database init skipped: {e}")

except ImportError:
    try:
        from auth_onboarding.routes import router as auth_router, init_db
        from auth_onboarding.admin import router as admin_router
        from auth_onboarding.owner_bootstrap import router as owner_bootstrap_router
        from auth_onboarding.invite import router as invite_router

        app.include_router(auth_router)
        app.include_router(admin_router)
        app.include_router(owner_bootstrap_router)
        app.include_router(invite_router)

        @app.on_event("startup")
        def startup_db():
            try:
                init_db()
            except Exception as e:
                print(f"Warning: Database init skipped: {e}")

    except Exception as e:
        import traceback

        print(f"Warning: Auth router not available: {e}")
        print("Full traceback:")
        traceback.print_exc()


# Include Athena costs router (tenant-specific CUR queries)
try:
    from api.secure.aws.athena_costs import router as athena_costs_router
    app.include_router(athena_costs_router)
except ImportError:
    try:
        from secure.aws.athena_costs import router as athena_costs_router
        app.include_router(athena_costs_router)
    except Exception as e:
        print(f"Warning: Athena costs router not available: {e}")

# Include ML routers
try:
    from api.routers.ml_anomalies import router as ml_anomalies_router
    from api.routers.ml_right_sizing import router as ml_right_sizing_router
    from api.routers.ml_forecasting import router as ml_forecasting_router
    app.include_router(ml_anomalies_router)
    app.include_router(ml_right_sizing_router)
    app.include_router(ml_forecasting_router)
except ImportError:
    try:
        from routers.ml_anomalies import router as ml_anomalies_router
        from routers.ml_right_sizing import router as ml_right_sizing_router
        from routers.ml_forecasting import router as ml_forecasting_router
        app.include_router(ml_anomalies_router)
        app.include_router(ml_right_sizing_router)
        app.include_router(ml_forecasting_router)
    except Exception as e:
        print(f"Warning: ML routers not available: {e}")


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"ok": True}


# ---------- ML Data Availability Check ----------
@app.get("/api/ml/data-availability")
def check_ml_data_availability(
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
):
    """Check how many days of cost data are available for ML training"""
    import time
    from botocore.config import Config
    
    _, tenant = resolve_tenant(session, authorization, tenantId)
    
    if not CUR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="CUR integration is not available on this deployment.",
        )
    
    try:
        # Get AWS session
        aws_session = assume_vendor_role(
            tenant.aws_role_arn, tenant.external_id, tenant.region or "us-east-1"
        )
        
        # Query to check date range
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
        
        # Execute Athena query
        athena = aws_session.client("athena", config=Config(retries={"max_attempts": 8}))
        query_params = {
            "QueryString": query,
            "QueryExecutionContext": {"Database": tenant.athena_db},
            "WorkGroup": tenant.athena_workgroup or "primary",
        }
        
        qid = athena.start_query_execution(**query_params)["QueryExecutionId"]
        
        # Wait for query to complete
        state = "RUNNING"
        timeout = time.time() + 60
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
            raise HTTPException(status_code=500, detail=f"Athena query failed: {error_msg}")
        
        # Get results
        rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
        if len(rows) < 2:
            raise HTTPException(status_code=500, detail="No results returned")
        
        # Parse results
        headers = [c["VarCharValue"] for c in rows[0]["Data"]]
        data_row = rows[1]["Data"]
        result = dict(zip(headers, [cell.get("VarCharValue", "") for cell in data_row]))
        
        earliest_date = result.get('earliest_date') or result.get('EARLIEST_DATE')
        latest_date = result.get('latest_date') or result.get('LATEST_DATE')
        unique_days = int(result.get('unique_days') or result.get('UNIQUE_DAYS') or 0)
        total_records = int(result.get('total_records') or result.get('TOTAL_RECORDS') or 0)
        
        if not earliest_date or not latest_date:
            raise HTTPException(status_code=500, detail="Could not determine date range")
        
        # Parse dates
        earliest = datetime.strptime(earliest_date[:10], '%Y-%m-%d')
        latest = datetime.strptime(latest_date[:10], '%Y-%m-%d')
        days_available = (latest - earliest).days + 1
        days_from_today = (datetime.utcnow() - latest).days if latest < datetime.utcnow() else 0
        
        # Determine recommendation
        sufficient = days_available >= 90
        recommendation = "train_90_days" if days_available >= 90 else "wait_for_more_data"
        if days_available >= 180:
            recommendation = "train_180_days"
        elif days_available >= 120:
            recommendation = "train_120_days"
        
        return {
            "earliest_date": earliest_date[:10],
            "latest_date": latest_date[:10],
            "days_available": days_available,
            "unique_days": unique_days,
            "total_records": total_records,
            "days_from_today": days_from_today,
            "sufficient_for_training": sufficient,
            "recommendation": recommendation,
            "message": (
                f"✅ You have {days_available} days of data. "
                + ("Sufficient for anomaly detection!" if sufficient else f"Need {90 - days_available} more days.")
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking data availability: {str(e)}")


@app.get("/health", include_in_schema=False)
def health_root():
    """Alias for container health checks that expect /health."""
    return {"ok": True}


health_router = APIRouter()


@health_router.get("/healthz", include_in_schema=False)
def healthz_api():
    return {"ok": True}


app.include_router(health_router, prefix="/api")


# ---------- Helper utilities ----------
DEFAULT_ALERT_THRESHOLD_MULTIPLIER = 1.2

# In-memory overrides / user-generated data (persisted storage would replace these)
user_alerts_storage: Dict[int, List[Dict[str, Any]]] = {}
dynamic_alert_overrides: Dict[str, Dict[str, Any]] = {}
optimization_status_overrides: Dict[str, Dict[str, Any]] = {}


def parse_time_range(value: str) -> int:
    mapping = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    return mapping.get(value, 30)


def ensure_user_settings(
    session: Session, user_id: int, tenant_id: Optional[int], email: str
) -> UserSettings:
    settings = session.exec(
        select(UserSettings).where(UserSettings.user_id == user_id)
    ).first()
    if settings is None:
        settings = UserSettings(
            user_id=user_id,
            tenant_id=tenant_id,
            notifications=default_notifications(),
            alerts=default_alerts(),
            preferences=default_preferences(),
            profile={"email": email, "name": email.split("@")[0]},
        )
        session.add(settings)
        session.commit()
        session.refresh(settings)
    elif not settings.profile:
        settings.profile = {"email": email, "name": email.split("@")[0]}
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings


def serialize_settings(settings: UserSettings) -> Dict[str, Any]:
    return {
        "notifications": settings.notifications or default_notifications(),
        "alerts": settings.alerts or default_alerts(),
        "preferences": settings.preferences or default_preferences(),
        "profile": settings.profile or {},
    }


def resolve_tenant(
    session: Session, authorization: str, tenant_id_override: Optional[int] = None
) -> Tuple[Dict[str, Any], Tenant]:
    ctx = get_current_ctx(authorization, session)

    if tenant_id_override is not None:
        tenant = session.get(Tenant, tenant_id_override)
        if tenant is None:
            raise HTTPException(status_code=404, detail="Tenant not found")
    elif ctx.role == "global_owner":
        tenant = session.exec(
            select(Tenant)
            .where(Tenant.aws_role_arn.isnot(None))
            .where(Tenant.athena_db.isnot(None))
            .where(Tenant.athena_table.isnot(None))
        ).first()
        if tenant is None:
            raise HTTPException(
                status_code=400,
                detail="No tenants have been connected yet. Please connect a tenant first.",
            )
    else:
        tenant = session.get(Tenant, ctx.tenant_id)
        if tenant is None:
            raise HTTPException(status_code=404, detail="Tenant not found")

    if (
        not tenant.aws_role_arn
        or not tenant.external_id
        or not tenant.athena_db
        or not tenant.athena_table
    ):
        raise HTTPException(
            status_code=400,
            detail="Tenant is not fully connected to AWS CUR. Please complete the connection.",
        )

    return ctx, tenant


def fetch_tenant_cost_data(tenant: Tenant, days: int) -> Dict[str, Any]:
    """
    Fetch cost data for a tenant (wrapper for service layer)
    Delegates to AWSCostService for business logic
    """
    if not CUR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="CUR integration is not available on this deployment.",
        )
    
    # Delegate to service layer
    return aws_cost_service.fetch_tenant_cost_data(tenant, days)


def build_dynamic_alerts(cost_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build dynamic alerts (wrapper for service layer)
    Delegates to AWSCostService for business logic
    """
    return aws_cost_service.build_dynamic_alerts(cost_summary, dynamic_alert_overrides)


def build_optimization_recommendations(cost_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build optimization recommendations (wrapper for service layer)
    Delegates to AWSCostService for business logic
    """
    return aws_cost_service.build_optimization_recommendations(cost_summary, optimization_status_overrides)


def get_user_alerts_for_tenant(tenant_id: int) -> List[Dict[str, Any]]:
    return user_alerts_storage.setdefault(tenant_id, [])


# ---------- Dashboard endpoint ----------
class ServiceCost(BaseModel):
    name: str
    cost: float
    percentage: float


class Dashboard(BaseModel):
    totalCost: float
    monthlyCost: float
    dailyCost: float
    savings: float
    alerts: int
    optimizationScore: int
    forecast: float
    topServices: List[ServiceCost] = []


@app.get("/api/dashboard", response_model=Dashboard)
def dashboard(
    timeRange: str = "7d",
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
):
    days = parse_time_range(timeRange)
    ctx, tenant = resolve_tenant(session, authorization, tenantId)
    cost_summary = fetch_tenant_cost_data(tenant, days)

    monthly_cost = (
        round(cost_summary["total_cost"] * (30 / days), 2)
        if days
        else cost_summary["total_cost"]
    )
    daily_cost = round(cost_summary["avg_daily"], 2)
    savings = round(cost_summary["total_cost"] * 0.18, 2)
    dynamic_alerts = build_dynamic_alerts(cost_summary)
    manual_alerts = get_user_alerts_for_tenant(tenant.id)
    optimizations = build_optimization_recommendations(cost_summary)

    # Simple heuristic for optimization score (lower spend => higher score)
    optimization_score = max(55, min(95, 100 - int(len(optimizations) * 3)))
    forecast = round(monthly_cost * 1.05, 2)

    top_services = [
        {"name": svc["name"], "cost": svc["cost"], "percentage": svc["percentage"]}
        for svc in cost_summary["services"][:4]
    ]

    return {
        "totalCost": cost_summary["total_cost"],
        "monthlyCost": monthly_cost,
        "dailyCost": daily_cost,
        "savings": savings,
        "alerts": len(dynamic_alerts) + len(manual_alerts),
        "optimizationScore": optimization_score,
        "forecast": forecast,
        "topServices": top_services,
    }


# ---------- Costs endpoints ----------


@app.get("/api/costs/trends")
def get_cost_trends(
    timeRange: str = "7d",
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
):
    days = parse_time_range(timeRange)
    _, tenant = resolve_tenant(session, authorization, tenantId)
    cost_summary = fetch_tenant_cost_data(tenant, days)
    return {"data": cost_summary["daily"], "period": timeRange}


@app.get("/api/costs/services")
def get_service_costs(
    timeRange: str = "7d",
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
):
    days = parse_time_range(timeRange)
    _, tenant = resolve_tenant(session, authorization, tenantId)
    cost_summary = fetch_tenant_cost_data(tenant, days)

    services_payload = []
    for svc in cost_summary["services"]:
        services_payload.append(
            {
                "name": svc["name"],
                "cost": svc["cost"],
                "percentage": svc["percentage"],
                "change": svc["trend"],
                "trend": svc["trend"],
            }
        )

    return {"services": services_payload, "total": cost_summary["total_cost"]}


# ---------- Alerts endpoints ----------
class Alert(BaseModel):
    id: str
    type: str
    severity: str
    message: str
    timestamp: str
    status: Optional[str] = "active"
    service: Optional[str] = "All"
    threshold: Optional[float] = 0
    currentValue: Optional[float] = 0
    title: Optional[str] = None
    region: Optional[str] = "All"


@app.get("/api/alerts")
def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
    timeRange: str = "30d",
):
    days = parse_time_range(timeRange)
    ctx, tenant = resolve_tenant(session, authorization, tenantId)
    cost_summary = fetch_tenant_cost_data(tenant, days)

    alerts = build_dynamic_alerts(cost_summary)
    manual_alerts = get_user_alerts_for_tenant(tenant.id)

    combined = alerts + manual_alerts
    if status and status != "all":
        combined = [a for a in combined if a.get("status") == status]
    if severity and severity != "all":
        combined = [a for a in combined if a.get("severity") == severity]

    return combined


class CreateAlertRequest(BaseModel):
    type: str
    severity: str
    message: str
    service: Optional[str] = "All"
    threshold: Optional[float] = 0
    currentValue: Optional[float] = 0


@app.post("/api/alerts")
def create_alert(
    alert: CreateAlertRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
):
    ctx, tenant = resolve_tenant(session, authorization, tenantId)
    tenant_alerts = get_user_alerts_for_tenant(tenant.id)

    alert_id = f"user-{uuid4().hex}"
    new_alert = {
        "id": alert_id,
        "type": alert.type,
        "severity": alert.severity,
        "title": alert.type.replace("_", " ").title(),
        "message": alert.message,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "active",
        "service": alert.service or "All",
        "threshold": alert.threshold or 0,
        "currentValue": alert.currentValue or 0,
        "region": "All",
        "createdBy": ctx.user_email,
    }
    tenant_alerts.append(new_alert)
    return new_alert


class UpdateAlertRequest(BaseModel):
    status: Optional[str] = None


@app.put("/api/alerts/{alert_id}")
def update_alert(
    alert_id: str,
    body: UpdateAlertRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
    timeRange: str = "30d",
):
    _, tenant = resolve_tenant(session, authorization, tenantId)
    tenant_alerts = get_user_alerts_for_tenant(tenant.id)

    for alert in tenant_alerts:
        if alert["id"] == alert_id:
            if body.status:
                alert["status"] = body.status
                alert["timestamp"] = datetime.utcnow().isoformat()
            return alert

    if alert_id.startswith("auto-"):
        override = dynamic_alert_overrides.setdefault(alert_id, {})
        if body.status:
            override["status"] = body.status
        cost_summary = fetch_tenant_cost_data(tenant, parse_time_range(timeRange))
        dynamic_alerts = build_dynamic_alerts(cost_summary)
        updated = next((a for a in dynamic_alerts if a["id"] == alert_id), None)
        if updated:
            return updated

    raise HTTPException(status_code=404, detail="Alert not found")


@app.delete("/api/alerts/{alert_id}")
def delete_alert(
    alert_id: str,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
):
    _, tenant = resolve_tenant(session, authorization, tenantId)
    tenant_alerts = get_user_alerts_for_tenant(tenant.id)

    for idx, alert in enumerate(tenant_alerts):
        if alert["id"] == alert_id:
            tenant_alerts.pop(idx)
            return {"success": True, "message": "Alert deleted"}

    if alert_id.startswith("auto-") and alert_id in dynamic_alert_overrides:
        dynamic_alert_overrides.pop(alert_id, None)
        return {"success": True, "message": "Alert override cleared"}

    raise HTTPException(status_code=404, detail="Alert not found")


# ---------- Optimizations endpoints ----------
class Optimization(BaseModel):
    id: str
    type: str
    service: str
    description: str
    potentialSavings: float
    impact: str
    effort: str
    status: str
    priority: Optional[str] = "medium"


@app.get("/api/optimizations")
def get_optimizations(
    service: Optional[str] = None,
    status: Optional[str] = None,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
    timeRange: str = "30d",
):
    _, tenant = resolve_tenant(session, authorization, tenantId)
    cost_summary = fetch_tenant_cost_data(tenant, parse_time_range(timeRange))
    recommendations = build_optimization_recommendations(cost_summary)

    if service and service != "all":
        recommendations = [r for r in recommendations if r.get("service") == service]
    if status and status != "all":
        recommendations = [r for r in recommendations if r.get("status") == status]

    return recommendations


@app.post("/api/optimizations/{opt_id}/apply")
def apply_optimization(
    opt_id: str,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
    tenantId: Optional[int] = Query(None, alias="tenantId"),
):
    resolve_tenant(session, authorization, tenantId)
    override = optimization_status_overrides.setdefault(opt_id, {})
    override["status"] = "applied"
    override["appliedAt"] = datetime.utcnow().isoformat()
    return {
        "success": True,
        "message": f"Optimization {opt_id} marked as applied.",
        "appliedAt": override["appliedAt"],
    }


# ---------- Settings & Profile endpoints ----------
class UpdateSettingsRequest(BaseModel):
    notifications: Optional[Dict[str, Any]] = None
    alerts: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class ChangePasswordRequest(BaseModel):
    currentPassword: str
    newPassword: str


@app.get("/api/settings")
def get_settings(
    authorization: str = Header(...), session: Session = Depends(get_session)
):
    ctx = get_current_ctx(authorization, session)
    settings = ensure_user_settings(session, ctx.user_id, ctx.tenant_id, ctx.user_email)
    return serialize_settings(settings)


@app.put("/api/settings")
def update_settings(
    settings: UpdateSettingsRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    ctx = get_current_ctx(authorization, session)
    user = session.get(User, ctx.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_settings = ensure_user_settings(
        session, ctx.user_id, ctx.tenant_id, ctx.user_email
    )

    if settings.notifications is not None:
        current = db_settings.notifications or default_notifications()
        current.update(settings.notifications)
        db_settings.notifications = current

    if settings.alerts is not None:
        current = db_settings.alerts or default_alerts()
        current.update(settings.alerts)
        db_settings.alerts = current

    if settings.preferences is not None:
        current = db_settings.preferences or default_preferences()
        current.update(settings.preferences)
        db_settings.preferences = current

    if settings.profile is not None:
        profile = db_settings.profile or {
            "email": user.email,
            "name": user.email.split("@")[0],
        }
        profile.update(settings.profile)
        new_email = profile.get("email")
        if new_email and new_email.lower() != user.email.lower():
            existing = session.exec(
                select(User).where(User.email == new_email.lower())
            ).first()
            if existing and existing.id != user.id:
                raise HTTPException(status_code=400, detail="Email is already in use")
            user.email = new_email.lower()
        db_settings.profile = profile

    db_settings.updated_at = datetime.utcnow()
    session.add(db_settings)
    session.add(user)
    session.commit()
    session.refresh(db_settings)

    return serialize_settings(db_settings)


@app.get("/api/user/profile")
def get_profile(
    authorization: str = Header(...), session: Session = Depends(get_session)
):
    ctx = get_current_ctx(authorization, session)
    user = session.get(User, ctx.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    settings = ensure_user_settings(session, ctx.user_id, ctx.tenant_id, ctx.user_email)
    profile = settings.profile or {}

    return {
        "id": user.id,
        "name": profile.get("name") or user.email.split("@")[0],
        "email": profile.get("email") or user.email,
        "role": ctx.role,
        "tenantId": ctx.tenant_id,
        "settings": serialize_settings(settings),
        "updatedAt": (
            settings.updated_at.isoformat()
            if hasattr(settings, "updated_at") and settings.updated_at
            else None
        ),
    }


@app.put("/api/user/profile")
def update_profile(
    body: UpdateProfileRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    ctx = get_current_ctx(authorization, session)
    user = session.get(User, ctx.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    settings = ensure_user_settings(session, ctx.user_id, ctx.tenant_id, ctx.user_email)
    profile = settings.profile or {
        "email": user.email,
        "name": user.email.split("@")[0],
    }

    if body.name is not None:
        profile["name"] = body.name

    if body.email is not None:
        new_email = body.email.lower()
        if new_email != user.email.lower():
            existing = session.exec(select(User).where(User.email == new_email)).first()
            if existing and existing.id != user.id:
                raise HTTPException(status_code=400, detail="Email is already in use")
            user.email = new_email
        profile["email"] = new_email

    settings.profile = profile
    settings.updated_at = datetime.utcnow()

    session.add(user)
    session.add(settings)
    session.commit()
    session.refresh(settings)

    return {
        "id": user.id,
        "name": profile.get("name") or user.email.split("@")[0],
        "email": profile.get("email") or user.email,
        "role": ctx.role,
        "settings": serialize_settings(settings),
    }


@app.put("/api/user/password")
def change_password(
    body: ChangePasswordRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    ctx = get_current_ctx(authorization, session)
    user = session.get(User, ctx.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(body.currentPassword, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(body.newPassword) < 8:
        raise HTTPException(
            status_code=400, detail="New password must be at least 8 characters long"
        )

    user.password_hash = hash_password(body.newPassword)
    session.add(user)
    session.commit()

    return {"success": True, "message": "Password updated successfully"}
