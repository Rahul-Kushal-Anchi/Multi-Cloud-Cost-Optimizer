"""
AWS Cost Service
Business logic for fetching and processing AWS cost data from CUR via Athena
"""

from typing import Dict, List, Any
from statistics import mean
from datetime import datetime
import logging

try:
    from api.auth_onboarding.models import Tenant
    from api.secure.aws.assume_role import assume_vendor_role
    from api.secure.aws.athena_costs import run_athena_query, cur_cost_query_sql
except ImportError:
    from auth_onboarding.models import Tenant
    from secure.aws.assume_role import assume_vendor_role
    from secure.aws.athena_costs import run_athena_query, cur_cost_query_sql

logger = logging.getLogger("api.services.aws_cost")

# Constants
DEFAULT_ALERT_THRESHOLD_MULTIPLIER = 1.3


class AWSCostService:
    """Service for fetching and processing AWS cost data"""
    
    def __init__(self):
        self.logger = logger
    
    def fetch_tenant_cost_data(self, tenant: Tenant, days: int) -> Dict[str, Any]:
        """
        Fetch cost data for a tenant from AWS CUR via Athena
        
        Args:
            tenant: Tenant model with AWS connection details
            days: Number of days to fetch
        
        Returns:
            Dict with services, daily data, total cost, and average daily cost
        """
        # Get AWS session using tenant credentials
        session = assume_vendor_role(
            tenant.aws_role_arn,
            tenant.external_id,
            tenant.region or "us-east-1"
        )
        
        workgroup = tenant.athena_workgroup or "primary"
        database = tenant.athena_db
        table = f"{tenant.athena_db}.{tenant.athena_table}"
        
        # Query service costs
        service_rows = run_athena_query(
            session,
            workgroup=workgroup,
            database=database,
            query=cur_cost_query_sql(table, days),
        )
        self.logger.info(
            "cur_fetch tenant=%s days=%s services_raw_sample=%s",
            tenant.id,
            days,
            service_rows[:3],
        )
        
        # Process service costs
        services = self._process_service_costs(service_rows)
        
        # Query daily costs
        daily_query = f"""
        SELECT 
          date_trunc('day', line_item_usage_start_date) AS day,
          SUM(COALESCE(CAST(line_item_unblended_cost AS double), 0)) AS cost
        FROM {table}
        WHERE line_item_usage_start_date >= date_add('day', -{days}, current_timestamp)
          AND "$path" LIKE '%.parquet'
        GROUP BY 1
        ORDER BY 1 ASC
        """
        
        daily_rows = run_athena_query(
            session, workgroup=workgroup, database=database, query=daily_query
        )
        self.logger.info(
            "cur_fetch tenant=%s days=%s daily_raw_sample=%s",
            tenant.id,
            days,
            daily_rows[:3],
        )
        
        # Process daily costs
        daily_data = self._process_daily_costs(daily_rows)
        
        total_cost = round(sum(item["cost"] for item in daily_data), 2)
        avg_daily = mean([item["cost"] for item in daily_data]) if daily_data else 0.0
        
        # Add forecast and savings to daily data
        for item in daily_data:
            item["forecast"] = (
                round(avg_daily * 1.08, 2) if avg_daily else round(item["cost"] * 1.05, 2)
            )
            item["savings"] = round(item["cost"] * 0.18, 2)
        
        return {
            "services": services,
            "daily": daily_data,
            "total_cost": total_cost,
            "avg_daily": avg_daily,
        }
    
    def _process_service_costs(self, service_rows: List[Dict]) -> List[Dict[str, Any]]:
        """Process raw service cost data from Athena"""
        services: List[Dict[str, Any]] = []
        total_service_cost = 0.0
        
        for row in service_rows:
            name = (
                row.get("service")
                or row.get("SERVICE")
                or row.get("product_product_name")
                or "Other"
            )
            try:
                cost = float(row.get("cost") or row.get("COST") or 0)
            except (TypeError, ValueError):
                cost = 0.0
            
            if cost <= 0:
                continue
            
            total_service_cost += cost
            services.append({
                "name": name.replace("Amazon ", "").replace("AWS ", ""),
                "cost": round(cost, 2),
            })
        
        # Calculate percentages and trends
        services.sort(key=lambda s: s["cost"], reverse=True)
        baseline_pct = (100 / len(services)) if services else 0.0
        
        for svc in services:
            svc["percentage"] = (
                round((svc["cost"] / total_service_cost) * 100, 2)
                if total_service_cost
                else 0.0
            )
            svc["trend"] = (
                round(svc["percentage"] - baseline_pct, 2) if baseline_pct else 0.0
            )
        
        return services
    
    def _process_daily_costs(self, daily_rows: List[Dict]) -> List[Dict[str, Any]]:
        """Process raw daily cost data from Athena"""
        daily_data: List[Dict[str, Any]] = []
        
        for row in daily_rows:
            day_raw = row.get("day") or row.get("DAY")
            cost_raw = row.get("cost") or row.get("COST") or 0
            
            try:
                cost_val = float(cost_raw)
            except (TypeError, ValueError):
                cost_val = 0.0
            
            day = day_raw[:10] if isinstance(day_raw, str) else ""
            daily_data.append({"date": day, "cost": round(cost_val, 2)})
        
        return daily_data
    
    def build_dynamic_alerts(self, cost_summary: Dict[str, Any], dynamic_alert_overrides: Dict = None) -> List[Dict[str, Any]]:
        """Build dynamic alerts based on cost patterns"""
        if dynamic_alert_overrides is None:
            dynamic_alert_overrides = {}
        
        alerts: List[Dict[str, Any]] = []
        daily_data = cost_summary["daily"]
        
        if not daily_data:
            return alerts
        
        latest = daily_data[-1]["cost"]
        previous_window = [item["cost"] for item in daily_data[:-1]] or [latest]
        previous_avg = mean(previous_window) if previous_window else latest
        
        # Cost spike detection
        if previous_avg and latest > previous_avg * DEFAULT_ALERT_THRESHOLD_MULTIPLIER:
            alerts.append({
                "id": "auto-cost-spike",
                "type": "cost_spike",
                "severity": "high",
                "title": "Cost spike detected",
                "message": f"Daily spend ${latest:,.2f} exceeded baseline ${previous_avg:,.2f}",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "active",
                "threshold": round(previous_avg * DEFAULT_ALERT_THRESHOLD_MULTIPLIER, 2),
                "currentValue": round(latest, 2),
                "service": "Overall",
                "region": "All",
            })
        
        # Cost drop detection
        if previous_avg and latest < previous_avg * 0.7:
            alerts.append({
                "id": "auto-sudden-drop",
                "type": "usage_drop",
                "severity": "medium",
                "title": "Significant drop in spend",
                "message": f"Latest spend ${latest:,.2f} is much lower than typical ${previous_avg:,.2f}",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "active",
                "threshold": round(previous_avg * 0.7, 2),
                "currentValue": round(latest, 2),
                "service": "Overall",
                "region": "All",
            })
        
        # Apply overrides
        return [
            {**alert, **dynamic_alert_overrides.get(alert["id"], {})} for alert in alerts
        ]
    
    def build_optimization_recommendations(self, cost_summary: Dict[str, Any], optimization_status_overrides: Dict = None) -> List[Dict[str, Any]]:
        """Build optimization recommendations based on cost data"""
        if optimization_status_overrides is None:
            optimization_status_overrides = {}
        
        recommendations: List[Dict[str, Any]] = []
        services = cost_summary["services"]
        
        # Per-service recommendations
        for index, service in enumerate(services[:5]):
            savings_estimate = round(service["cost"] * 0.25, 2)
            impact = (
                "high" if service["percentage"] >= 25
                else "medium" if service["percentage"] >= 10
                else "low"
            )
            effort = "low" if index == 0 else "medium" if index <= 2 else "high"
            
            rec_id = f"opt-{service['name'].lower().replace(' ', '-')}"
            recommendations.append({
                "id": rec_id,
                "type": "cost_optimization",
                "service": service["name"],
                "description": f"Review {service['name']} spend (${service['cost']:,.2f}) for rightsizing and savings opportunities.",
                "potentialSavings": savings_estimate,
                "impact": impact,
                "effort": effort,
                "status": optimization_status_overrides.get(rec_id, {}).get("status", "recommended"),
                "priority": "high" if impact == "high" else "medium" if impact == "medium" else "low",
            })
        
        # Reserved Instance recommendation
        if cost_summary["total_cost"] > 0:
            rec_id = "opt-reserved-instance-review"
            recommendations.append({
                "id": rec_id,
                "type": "purchase_planning",
                "service": "EC2/RDS",
                "description": "Evaluate Reserved Instances or Savings Plans to lock in savings for steady workloads.",
                "potentialSavings": round(cost_summary["total_cost"] * 0.18, 2),
                "impact": "medium",
                "effort": "medium",
                "status": optimization_status_overrides.get(rec_id, {}).get("status", "recommended"),
                "priority": "medium",
            })
        
        return recommendations


# Singleton instance
aws_cost_service = AWSCostService()

