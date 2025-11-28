"""
ML Right-Sizing API Endpoints
Recommend optimal EC2 instance types based on REAL CloudWatch metrics
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select

try:
    from api.ml.right_sizer import right_sizer
    from api.ml.models import Recommendation
    from api.secure.aws.cloudwatch import get_ec2_instances, collect_all_instance_metrics
    from api.auth_onboarding.models import Tenant
    from api.auth_onboarding.routes import get_session
    from api.auth_onboarding.current import get_current_ctx
    from api.secure.aws.assume_role import assume_vendor_role
except ImportError:
    from ml.right_sizer import right_sizer
    from ml.models import Recommendation
    from secure.aws.cloudwatch import get_ec2_instances, collect_all_instance_metrics
    from auth_onboarding.models import Tenant
    from auth_onboarding.routes import get_session
    from auth_onboarding.current import get_current_ctx
    from secure.aws.assume_role import assume_vendor_role

router = APIRouter(prefix="/api/ml", tags=["ml-right-sizing"])


@router.get("/right-sizing")
async def get_right_sizing_recommendations(
    lookback_days: int = 14,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """
    Get right-sizing recommendations based on REAL CloudWatch metrics
    Analyzes actual CPU/memory usage to recommend optimal instance types
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
    
    if not tenant or not tenant.aws_role_arn:
        raise HTTPException(
            status_code=400,
            detail="No AWS connection configured"
        )
    
    try:
        # Get AWS session
        aws_session = assume_vendor_role(
            tenant.aws_role_arn,
            tenant.external_id,
            tenant.region or "us-east-1"
        )
        
        # Get all EC2 instances
        logger.info(f"Fetching EC2 instances for tenant {tenant.id}")
        instances = get_ec2_instances(aws_session)
        
        if not instances:
            return {
                "recommendations": [],
                "total_potential_savings": 0.0,
                "message": "No EC2 instances found in your AWS account"
            }
        
        logger.info(f"Found {len(instances)} EC2 instances")
        
        # Collect CloudWatch metrics for all instances
        logger.info(f"Collecting CloudWatch metrics (last {lookback_days} days)...")
        metrics_df = collect_all_instance_metrics(aws_session, lookback_days)
        
        if metrics_df.empty:
            return {
                "recommendations": [],
                "total_potential_savings": 0.0,
                "message": "No CloudWatch metrics available. Instances may be stopped or metrics not available yet."
            }
        
        logger.info(f"Collected metrics for {metrics_df['instance_id'].nunique()} instances")
        
        # Extract features from metrics
        from api.ml.features import extract_utilization_features
        instance_features = extract_utilization_features(metrics_df)
        
        # Generate recommendations for each instance
        recommendations = []
        total_savings = 0.0
        
        for _, row in instance_features.iterrows():
            instance_id = row['instance_id']
            
            # Find instance details
            instance = next((i for i in instances if i['instance_id'] == instance_id), None)
            if not instance or instance['state'] != 'running':
                continue
            
            current_type = instance.get('instance_type', 'unknown')
            
            # Prepare metrics dict
            metrics_dict = {
                'cpu_mean': row.get('cpu_mean', 0),
                'cpu_p95': row.get('cpu_p95', 0),
                'cpu_p99': row.get('cpu_p99', 0),
                'memory_mean': row.get('memory_mean'),
                'memory_p95': row.get('memory_p95'),
                'memory_p99': row.get('memory_p99'),
                'cpu_std': row.get('cpu_std', 0),
            }
            
            # Get recommendation
            recommendation = right_sizer.analyze_instance(
                instance_id,
                current_type,
                metrics_dict
            )
            
            if recommendation:
                recommendations.append(recommendation)
                total_savings += recommendation['estimated_savings']
                
                # Save to database
                rec_record = Recommendation(
                    tenant_id=tenant.id,
                    resource_id=instance_id,
                    resource_type="ec2",
                    current_instance_type=current_type,
                    recommended_instance_type=recommendation['recommended_instance_type'],
                    current_monthly_cost=recommendation['current_monthly_cost'],
                    recommended_monthly_cost=recommendation['recommended_monthly_cost'],
                    estimated_savings=recommendation['estimated_savings'],
                    savings_percentage=recommendation['savings_percentage'],
                    risk_level=recommendation['risk_level'],
                    confidence_score=recommendation['confidence_score'],
                    reasoning=recommendation['reasoning'],
                    cpu_utilization_avg=recommendation.get('cpu_utilization_avg'),
                    cpu_utilization_p95=recommendation.get('cpu_utilization_p95'),
                    memory_utilization_avg=recommendation.get('memory_utilization_avg'),
                    memory_utilization_p95=recommendation.get('memory_utilization_p95'),
                    status="pending",
                    model_version="1.0.0",
                )
                session.add(rec_record)
        
        session.commit()
        
        logger.info(f"Generated {len(recommendations)} recommendations, total savings: ${total_savings:.2f}/month")
        
        return {
            "recommendations": recommendations,
            "total_potential_savings": round(total_savings, 2),
            "instances_analyzed": len(instances),
            "recommendations_generated": len(recommendations),
            "lookback_days": lookback_days,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.get("/recommendations")
async def get_saved_recommendations(
    status: Optional[str] = None,
    authorization: str = Header(...),
    session: Session = Depends(get_session),
):
    """Get saved right-sizing recommendations from database"""
    ctx = get_current_ctx(authorization, session)
    
    if ctx.role == "global_owner":
        tenant = session.exec(
            select(Tenant).where(Tenant.aws_role_arn.isnot(None))
        ).first()
    else:
        tenant = session.get(Tenant, ctx.tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=400, detail="No tenant found")
    
    # Query recommendations
    query = select(Recommendation).where(Recommendation.tenant_id == tenant.id)
    
    if status:
        query = query.where(Recommendation.status == status)
    
    query = query.order_by(Recommendation.created_at.desc())
    
    recommendations = session.exec(query).all()
    
    return {
        "recommendations": [
            {
                "id": r.id,
                "instance_id": r.resource_id,
                "current_type": r.current_instance_type,
                "recommended_type": r.recommended_instance_type,
                "monthly_savings": float(r.estimated_savings),
                "savings_percentage": r.savings_percentage,
                "risk_level": r.risk_level,
                "confidence": r.confidence_score,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
            }
            for r in recommendations
        ],
        "total": len(recommendations),
    }


