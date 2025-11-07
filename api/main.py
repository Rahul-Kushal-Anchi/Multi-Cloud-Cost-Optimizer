from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

# Secure deps for real CUR
import sys
import os
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
        print(f"Warning: CUR modules not available: {e}")
        CUR_AVAILABLE = False
except Exception as e:
    print(f"Warning: CUR modules not available: {e}")
    CUR_AVAILABLE = False

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

app = FastAPI(title="Cost Optimizer API", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

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

@app.get("/healthz")
def healthz(): 
    return {"ok": True}



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
def dashboard(timeRange: str = "7d"):
    # Use real Cost Explorer data if available
    if COST_EXPLORER_AVAILABLE:
        try:
            days = 7 if timeRange == "7d" else (30 if timeRange == "30d" else 90)
            client = get_cost_client()
            
            # Get real service costs
            service_costs = client.get_service_costs(days=days)
            total = sum(service_costs.values())
            
            # Calculate monthly and daily
            monthly_cost = total * (30 / days)
            daily_cost = total / days
            
            # Get top services
            top_services = []
            for name, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:4]:
                if cost > 0:
                    percentage = round((cost / total * 100), 1) if total > 0 else 0
                    clean_name = name.replace("Amazon ", "").replace("AWS ", "")
                    top_services.append({
                        "name": clean_name,
                        "cost": round(cost, 2),
                        "percentage": percentage
                    })
            
            return {
                "totalCost": round(total, 2),
                "monthlyCost": round(monthly_cost, 2),
                "dailyCost": round(daily_cost, 2),
                "savings": round(total * 0.20, 2),  # 20% potential savings estimate
                "alerts": 0,  # Will be calculated from actual alerts
                "optimizationScore": 85,
                "forecast": round(monthly_cost * 1.08, 2),  # 8% forecast increase
                "topServices": top_services[:4] if top_services else []
            }
        except Exception as e:
            print(f"Error fetching real dashboard data: {e}")
            raise HTTPException(status_code=503, detail=f"Unable to fetch cost data: {str(e)}")
    
    # No Cost Explorer available
    raise HTTPException(status_code=503, detail="Cost Explorer not available. Please connect your AWS account.")

# ---------- Costs endpoints ----------

@app.get("/api/costs/trends")
def get_cost_trends(timeRange: str = "7d"):
    # Use real Cost Explorer data if available
    if COST_EXPLORER_AVAILABLE:
        try:
            days = 7 if timeRange == "7d" else (30 if timeRange == "30d" else 90)
            client = get_cost_client()
            trends = client.get_cost_trends(days=days)
            return {"data": trends, "period": timeRange}
        except Exception as e:
            print(f"Error fetching real cost trends: {e}")
            raise HTTPException(status_code=503, detail=f"Unable to fetch cost trends: {str(e)}")
    
    # No Cost Explorer available
    raise HTTPException(status_code=503, detail="Cost Explorer not available. Please connect your AWS account.")

@app.get("/api/costs/services")
def get_service_costs(timeRange: str = "7d"):
    # Use real Cost Explorer data if available
    if COST_EXPLORER_AVAILABLE:
        try:
            days = 7 if timeRange == "7d" else (30 if timeRange == "30d" else 90)
            client = get_cost_client()
            service_costs = client.get_service_costs(days=days)
            
            # Convert to required format
            total = sum(service_costs.values())
            services = []
            for name, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:10]:
                if cost > 0:  # Only include services with actual costs
                    percentage = round((cost / total * 100), 1) if total > 0 else 0
                    # Map AWS service names to cleaner names
                    clean_name = name.replace("Amazon ", "").replace("AWS ", "")
                    services.append({
                        "name": clean_name,
                        "cost": round(cost, 2),
                        "percentage": percentage,
                        "change": 0.0  # Could calculate from historical data
                    })
            
            return {"services": services, "total": round(total, 2)}
        except Exception as e:
            print(f"Error fetching real service costs: {e}")
            raise HTTPException(status_code=503, detail=f"Unable to fetch service costs: {str(e)}")
    
    # No Cost Explorer available
    raise HTTPException(status_code=503, detail="Cost Explorer not available. Please connect your AWS account.")

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

# In-memory storage for alerts (replace with database in production)
alerts_storage = [
    {
        "id": "1",
        "type": "cost_spike",
        "severity": "high",
        "message": "Cost increased by 200% in the last 24 hours",
        "timestamp": datetime.now().isoformat(),
        "status": "active",
        "service": "EC2",
        "threshold": 5000,
        "currentValue": 6500
    },
    {
        "id": "2",
        "type": "budget_exceeded",
        "severity": "medium",
        "message": "Monthly budget exceeded by 15%",
        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
        "status": "active",
        "service": "Overall",
        "threshold": 10000,
        "currentValue": 11500
    },
    {
        "id": "3",
        "type": "anomaly_detected",
        "severity": "low",
        "message": "Unusual spending pattern detected in S3",
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
        "status": "resolved",
        "service": "S3",
        "threshold": 2000,
        "currentValue": 2200
    }
]

@app.get("/api/alerts")
def get_alerts(status: Optional[str] = None, severity: Optional[str] = None):
    filtered = alerts_storage.copy()
    if status and status != "all":
        filtered = [a for a in filtered if a.get("status") == status]
    if severity and severity != "all":
        filtered = [a for a in filtered if a.get("severity") == severity]
    return filtered

class CreateAlertRequest(BaseModel):
    type: str
    severity: str
    message: str
    service: Optional[str] = "All"
    threshold: Optional[float] = 0
    currentValue: Optional[float] = 0

@app.post("/api/alerts")
def create_alert(alert: CreateAlertRequest):
    new_alert = {
        "id": str(len(alerts_storage) + 1),
        "type": alert.type,
        "severity": alert.severity,
        "message": alert.message,
        "timestamp": datetime.now().isoformat(),
        "status": "active",
        "service": alert.service,
        "threshold": alert.threshold,
        "currentValue": alert.currentValue
    }
    alerts_storage.append(new_alert)
    return new_alert

class UpdateAlertRequest(BaseModel):
    status: Optional[str] = None

@app.put("/api/alerts/{alert_id}")
def update_alert(alert_id: str, body: UpdateAlertRequest):
    for alert in alerts_storage:
        if alert["id"] == alert_id:
            if body.status:
                alert["status"] = body.status
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")

@app.delete("/api/alerts/{alert_id}")
def delete_alert(alert_id: str):
    global alerts_storage
    alerts_storage = [a for a in alerts_storage if a["id"] != alert_id]
    return {"success": True, "message": "Alert deleted"}

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
def get_optimizations(service: Optional[str] = None, status: Optional[str] = None):
    optimizations = [
        {
            "id": "1",
            "type": "resize_instance",
            "service": "EC2",
            "description": "Resize t3.large to t3.medium for 30% savings",
            "potentialSavings": 1500.0,
            "impact": "low",
            "effort": "low",
            "status": "recommended",
            "priority": "high"
        },
        {
            "id": "2",
            "type": "delete_unused_resources",
            "service": "EC2",
            "description": "Delete 5 unattached EBS volumes",
            "potentialSavings": 800.0,
            "impact": "none",
            "effort": "low",
            "status": "recommended",
            "priority": "medium"
        },
        {
            "id": "3",
            "type": "enable_s3_lifecycle",
            "service": "S3",
            "description": "Enable lifecycle policies for old data",
            "potentialSavings": 600.0,
            "impact": "none",
            "effort": "medium",
            "status": "recommended",
            "priority": "medium"
        },
        {
            "id": "4",
            "type": "reserved_instances",
            "service": "RDS",
            "description": "Purchase Reserved Instances for predictable workloads",
            "potentialSavings": 2500.0,
            "impact": "low",
            "effort": "medium",
            "status": "recommended",
            "priority": "high"
        },
        {
            "id": "5",
            "type": "lambda_provisioned",
            "service": "Lambda",
            "description": "Enable provisioned concurrency for consistent performance",
            "potentialSavings": 300.0,
            "impact": "low",
            "effort": "high",
            "status": "draft",
            "priority": "low"
        }
    ]
    filtered = optimizations
    if service:
        filtered = [o for o in filtered if o.get("service") == service]
    if status:
        filtered = [o for o in filtered if o.get("status") == status]
    return filtered

@app.post("/api/optimizations/{opt_id}/apply")
def apply_optimization(opt_id: str):
    return {
        "success": True,
        "message": f"Optimization {opt_id} applied successfully",
        "appliedAt": datetime.now().isoformat()
    }

# ---------- Settings endpoint ----------
# In-memory settings storage (replace with database in production)
settings_storage = {
    "notifications": {
        "email": True,
        "push": True,
        "sms": False
    },
    "alerts": {
        "costSpike": True,
        "budgetExceeded": True,
        "anomaly": True,
        "optimization": False
    },
    "preferences": {
        "theme": "light",
        "timezone": "UTC",
        "currency": "USD",
        "language": "en"
    },
    "profile": {
        "name": "",
        "email": ""
    }
}

@app.get("/api/settings")
def get_settings():
    return settings_storage

class UpdateSettingsRequest(BaseModel):
    notifications: Optional[dict] = None
    alerts: Optional[dict] = None
    preferences: Optional[dict] = None
    profile: Optional[dict] = None

@app.put("/api/settings")
def update_settings(settings: UpdateSettingsRequest):
    global settings_storage
    if settings.notifications:
        settings_storage["notifications"].update(settings.notifications)
    if settings.alerts:
        settings_storage["alerts"].update(settings.alerts)
    if settings.preferences:
        settings_storage["preferences"].update(settings.preferences)
    if settings.profile:
        settings_storage["profile"].update(settings.profile)
    return settings_storage

@app.get("/api/user/profile")
def get_profile(authorization: str = Header(None)):
    """Get user profile - requires authentication"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        from api.auth_onboarding.current import get_current_ctx
        from api.auth_onboarding.routes import get_session
        ctx = get_current_ctx(authorization, next(get_session()))
        
        return {
            "id": ctx.user_id,
            "name": ctx.user_email.split("@")[0],  # Use email prefix as name
            "email": ctx.user_email,
            "role": ctx.role,
            "createdAt": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
