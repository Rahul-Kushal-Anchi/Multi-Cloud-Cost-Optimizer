"""
ML Anomaly Detection API Endpoints
Train and detect cost anomalies using machine learning
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
import pandas as pd

try:
    from api.ml.anomaly_detector import anomaly_detector
    from api.ml.models import MLModel, Anomaly
    from api.auth_onboarding.models import Tenant
    from api.auth_onboarding.routes import get_session
    from api.auth_onboarding.current import get_current_ctx
    from api.secure.aws.athena_costs import run_athena_query
    from api.secure.aws.assume_role import assume_vendor_role
except ImportError:
    from ml.anomaly_detector import anomaly_detector
    from ml.models import MLModel, Anomaly
    from auth_onboarding.models import Tenant
    from auth_onboarding.routes import get_session
    from auth_onboarding.current import get_current_ctx
    from secure.aws.athena_costs import run_athena_query
    from secure.aws.assume_role import assume_vendor_role

router = APIRouter(prefix="/api/ml", tags=["ml-anomalies"])


class TrainRequest(BaseModel):
    lookback_days: int = 90
    contamination: float = 0.1


class DetectRequest(BaseModel):
    lookback_days: int = 7
    threshold: float = -0.1


@router.post("/anomalies/train")
async def train_anomaly_model(
    request: TrainRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """
    Train anomaly detection model on historical cost data
    Fetches REAL data from AWS CUR via Athena
    """
    # Get current user context
    ctx = get_current_ctx(authorization, session)
    
    # Get tenant
    if ctx.role == "global_owner":
        # Global owner: find first connected tenant
        tenant = session.exec(
            select(Tenant)
            .where(Tenant.aws_role_arn.isnot(None))
            .where(Tenant.athena_db.isnot(None))
        ).first()
    else:
        tenant = session.get(Tenant, ctx.tenant_id)
    
    if not tenant or not tenant.aws_role_arn:
        raise HTTPException(
            status_code=400,
            detail="No AWS connection configured. Please connect AWS first."
        )
    
    try:
        # Fetch REAL cost data from AWS CUR
        aws_session = assume_vendor_role(
            tenant.aws_role_arn,
            tenant.external_id,
            tenant.region or "us-east-1"
        )
        
        # Query for daily costs
        table = f"{tenant.athena_db}.{tenant.athena_table}"
        query = f"""
        SELECT
          date(line_item_usage_start_date) AS date,
          SUM(CAST(line_item_unblended_cost AS double)) AS cost
        FROM {table}
        WHERE line_item_usage_start_date >= date_add('day', -{request.lookback_days}, current_timestamp)
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
                detail=f"Insufficient data: only {len(results) if results else 0} days available. Need at least 30 days."
            )
        
        # Convert to DataFrame
        cost_data = pd.DataFrame(results)
        cost_data['date'] = pd.to_datetime(cost_data['date'])
        cost_data['cost'] = pd.to_numeric(cost_data['cost'], errors='coerce').fillna(0)
        cost_data = cost_data.sort_values('date')
        
        # Train model
        training_summary = anomaly_detector.train(cost_data, request.lookback_days)
        
        # Save model metadata to database
        model_record = MLModel(
            tenant_id=tenant.id,
            model_type="anomaly_detection",
            version="1.0.0",
            trained_at=datetime.utcnow(),
            training_data_start=cost_data['date'].min(),
            training_data_end=cost_data['date'].max(),
            training_data_days=len(cost_data),
            hyperparameters=f"contamination={request.contamination}",
            is_active=True,
        )
        session.add(model_record)
        session.commit()
        session.refresh(model_record)
        
        # Save model to disk
        model_path = f"/tmp/anomaly_model_tenant_{tenant.id}.pkl"
        anomaly_detector.save_model(model_path)
        
        return {
            "success": True,
            "message": "Anomaly detection model trained successfully",
            "model_id": model_record.id,
            **training_summary,
            "data_quality": {
                "earliest_date": cost_data['date'].min().strftime('%Y-%m-%d'),
                "latest_date": cost_data['date'].max().strftime('%Y-%m-%d'),
                "total_cost": float(cost_data['cost'].sum()),
                "avg_daily_cost": float(cost_data['cost'].mean()),
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error training model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")


@router.post("/anomalies/detect")
async def detect_anomalies(
    request: DetectRequest,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """
    Detect anomalies in recent cost data
    Uses trained model to identify unusual spending patterns
    """
    # Get current user context
    ctx = get_current_ctx(authorization, session)
    
    # Get tenant
    if ctx.role == "global_owner":
        tenant = session.exec(
            select(Tenant)
            .where(Tenant.aws_role_arn.isnot(None))
            .where(Tenant.athena_db.isnot(None))
        ).first()
    else:
        tenant = session.get(Tenant, ctx.tenant_id)
    
    if not tenant or not tenant.aws_role_arn:
        raise HTTPException(
            status_code=400,
            detail="No AWS connection configured"
        )
    
    if not anomaly_detector.is_trained:
        raise HTTPException(
            status_code=400,
            detail="Model not trained. Please train the model first using POST /api/ml/anomalies/train"
        )
    
    try:
        # Fetch recent cost data
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
        WHERE line_item_usage_start_date >= date_add('day', -{request.lookback_days}, current_timestamp)
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
        
        if not results:
            return {
                "anomalies": [],
                "message": "No cost data available for detection"
            }
        
        # Convert to DataFrame
        cost_data = pd.DataFrame(results)
        cost_data['date'] = pd.to_datetime(cost_data['date'])
        cost_data['cost'] = pd.to_numeric(cost_data['cost'], errors='coerce').fillna(0)
        cost_data = cost_data.sort_values('date')
        
        # Detect anomalies
        anomalies = anomaly_detector.detect_anomalies(cost_data, request.threshold)
        
        # Save anomalies to database
        for anomaly in anomalies:
            anomaly_record = Anomaly(
                tenant_id=tenant.id,
                detected_at=datetime.utcnow(),
                anomaly_date=datetime.strptime(anomaly['date'], '%Y-%m-%d'),
                anomaly_score=anomaly['anomaly_score'],
                anomaly_type=anomaly['anomaly_type'],
                severity=anomaly['severity'],
                cost_after=anomaly['cost'],
                status="detected",
                model_version="1.0.0",
            )
            session.add(anomaly_record)
        
        session.commit()
        
        return {
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "detection_date": datetime.utcnow().isoformat(),
            "data_range": {
                "start": cost_data['date'].min().strftime('%Y-%m-%d'),
                "end": cost_data['date'].max().strftime('%Y-%m-%d'),
                "days": len(cost_data),
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error detecting anomalies: {str(e)}")


@router.get("/anomalies")
async def get_anomalies(
    days: int = 30,
    severity: Optional[str] = None,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """
    Get detected anomalies for the tenant
    Returns anomalies from the database
    """
    # Get current user context
    ctx = get_current_ctx(authorization, session)
    
    # Get tenant
    if ctx.role == "global_owner":
        tenant = session.exec(
            select(Tenant)
            .where(Tenant.aws_role_arn.isnot(None))
        ).first()
    else:
        tenant = session.get(Tenant, ctx.tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=400, detail="No tenant found")
    
    # Query anomalies
    query = select(Anomaly).where(Anomaly.tenant_id == tenant.id)
    
    # Filter by date range
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.where(Anomaly.anomaly_date >= cutoff_date)
    
    # Filter by severity
    if severity:
        query = query.where(Anomaly.severity == severity)
    
    # Order by date descending
    query = query.order_by(Anomaly.anomaly_date.desc())
    
    anomalies = session.exec(query).all()
    
    return {
        "anomalies": [
            {
                "id": a.id,
                "date": a.anomaly_date.strftime('%Y-%m-%d'),
                "anomaly_score": float(a.anomaly_score),
                "anomaly_type": a.anomaly_type,
                "severity": a.severity,
                "cost": float(a.cost_after) if a.cost_after else 0.0,
                "affected_service": a.affected_service,
                "status": a.status,
                "detected_at": a.detected_at.isoformat(),
            }
            for a in anomalies
        ],
        "total": len(anomalies),
        "filters": {
            "days": days,
            "severity": severity,
        }
    }


@router.get("/anomalies/model-status")
async def get_model_status(
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """Get status of the anomaly detection model"""
    ctx = get_current_ctx(authorization, session)
    
    if ctx.role == "global_owner":
        tenant = session.exec(
            select(Tenant).where(Tenant.aws_role_arn.isnot(None))
        ).first()
    else:
        tenant = session.get(Tenant, ctx.tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=400, detail="No tenant found")
    
    # Get latest model from database
    latest_model = session.exec(
        select(MLModel)
        .where(MLModel.tenant_id == tenant.id)
        .where(MLModel.model_type == "anomaly_detection")
        .where(MLModel.is_active == True)
        .order_by(MLModel.trained_at.desc())
    ).first()
    
    return {
        "is_trained": anomaly_detector.is_trained,
        "training_date": anomaly_detector.training_date.isoformat() if anomaly_detector.training_date else None,
        "feature_names": anomaly_detector.feature_names,
        "model_in_database": latest_model is not None,
        "database_model": {
            "id": latest_model.id,
            "version": latest_model.version,
            "trained_at": latest_model.trained_at.isoformat(),
            "training_days": latest_model.training_data_days,
        } if latest_model else None,
    }


