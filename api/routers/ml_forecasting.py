"""
ML Cost Forecasting API Endpoints
Predict future costs using time series forecasting on REAL historical data
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
import pandas as pd

try:
    from api.ml.forecaster import cost_forecaster, PROPHET_AVAILABLE
    from api.ml.models import Forecast
    from api.auth_onboarding.models import Tenant
    from api.auth_onboarding.routes import get_session
    from api.auth_onboarding.current import get_current_ctx
    from api.secure.aws.athena_costs import run_athena_query
    from api.secure.aws.assume_role import assume_vendor_role
except ImportError:
    from ml.forecaster import cost_forecaster, PROPHET_AVAILABLE
    from ml.models import Forecast
    from auth_onboarding.models import Tenant
    from auth_onboarding.routes import get_session
    from auth_onboarding.current import get_current_ctx
    from secure.aws.athena_costs import run_athena_query
    from secure.aws.assume_role import assume_vendor_role

router = APIRouter(prefix="/api/ml", tags=["ml-forecasting"])


class ForecastRequest(BaseModel):
    training_days: int = 90
    forecast_days: int = 30


@router.post("/forecast/train")
async def train_forecast_model(
    request: ForecastRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """Train cost forecasting model on REAL historical data"""
    ctx = get_current_ctx(authorization, session)
    
    if ctx.role == "global_owner":
        tenant = session.exec(
            select(Tenant).where(Tenant.aws_role_arn.isnot(None))
        ).first()
    else:
        tenant = session.get(Tenant, ctx.tenant_id)
    
    if not tenant or not tenant.aws_role_arn:
        raise HTTPException(status_code=400, detail="No AWS connection configured")
    
    try:
        # Fetch REAL cost data from AWS CUR
        aws_session = assume_vendor_role(
            tenant.aws_role_arn,
            tenant.external_id,
            tenant.region or "us-east-1"
        )
        
        table = f"{tenant.athena_db}.{tenant.athena_table}"
        query = f"""
        SELECT
          date(line_item_usage_start_date) AS date,
          SUM(CAST(line_item_unblended_cost AS double)) AS cost
        FROM {table}
        WHERE line_item_usage_start_date >= date_add('day', -{request.training_days}, current_timestamp)
          AND "$path" LIKE '%.parquet'
        GROUP BY date(line_item_usage_start_date)
        ORDER BY date ASC
        """
        
        results = run_athena_query(
            aws_session,
            query,
            tenant.athena_db,
            tenant.athena_workgroup or "primary"
        )
        
        if not results or len(results) < 30:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data: {len(results) if results else 0} days. Need at least 30 days."
            )
        
        # Convert to DataFrame
        cost_data = pd.DataFrame(results)
        cost_data['date'] = pd.to_datetime(cost_data['date'])
        cost_data['cost'] = pd.to_numeric(cost_data['cost'], errors='coerce').fillna(0)
        
        # Train model
        training_summary = cost_forecaster.train(cost_data)
        
        return {
            "success": True,
            "message": "Forecasting model trained successfully",
            **training_summary,
            "prophet_available": PROPHET_AVAILABLE,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")


@router.get("/forecast")
async def get_cost_forecast(
    days: int = 30,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """Get cost forecast for specified period"""
    ctx = get_current_ctx(authorization, session)
    
    if ctx.role == "global_owner":
        tenant = session.exec(
            select(Tenant).where(Tenant.aws_role_arn.isnot(None))
        ).first()
    else:
        tenant = session.get(Tenant, ctx.tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=400, detail="No tenant found")
    
    if not cost_forecaster.is_trained:
        raise HTTPException(
            status_code=400,
            detail="Model not trained. Train the model first using POST /api/ml/forecast/train"
        )
    
    try:
        # Generate forecast
        forecast_summary = cost_forecaster.get_forecast_summary(days)
        
        # Save forecasts to database
        for forecast in forecast_summary['forecasts']:
            forecast_record = Forecast(
                tenant_id=tenant.id,
                forecast_date=datetime.strptime(forecast['date'], '%Y-%m-%d'),
                forecasted_cost=forecast['forecasted_cost'],
                confidence_lower=forecast['confidence_lower'],
                confidence_upper=forecast['confidence_upper'],
                trend=forecast['trend'],
                model_version="1.0.0",
            )
            session.add(forecast_record)
        
        session.commit()
        
        return forecast_summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")

