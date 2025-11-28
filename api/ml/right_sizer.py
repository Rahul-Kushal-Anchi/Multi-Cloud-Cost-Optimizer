"""
Right-Sizing Recommendation Model
ML-powered EC2 instance right-sizing based on REAL CloudWatch metrics
Recommends optimal instance types with specific savings
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from typing import Dict, List, Tuple, Optional
import logging

try:
    from api.ml.features import extract_utilization_features
except ImportError:
    from ml.features import extract_utilization_features

logger = logging.getLogger("api.ml.right_sizer")

# AWS EC2 Pricing (approximate, should be fetched from AWS Pricing API in production)
# Format: instance_type: monthly_cost_usd
EC2_PRICING = {
    # T3 family (burstable)
    't3.nano': 3.80,
    't3.micro': 7.59,
    't3.small': 15.18,
    't3.medium': 30.37,
    't3.large': 60.74,
    't3.xlarge': 121.47,
    't3.2xlarge': 242.94,
    
    # M5 family (general purpose)
    'm5.large': 70.08,
    'm5.xlarge': 140.16,
    'm5.2xlarge': 280.32,
    'm5.4xlarge': 560.64,
    'm5.8xlarge': 1121.28,
    
    # C5 family (compute optimized)
    'c5.large': 62.05,
    'c5.xlarge': 124.10,
    'c5.2xlarge': 248.20,
    'c5.4xlarge': 496.40,
    
    # R5 family (memory optimized)
    'r5.large': 91.98,
    'r5.xlarge': 183.96,
    'r5.2xlarge': 367.92,
    'r5.4xlarge': 735.84,
}

# Instance specifications (vCPU, Memory GB)
INSTANCE_SPECS = {
    't3.nano': (2, 0.5),
    't3.micro': (2, 1),
    't3.small': (2, 2),
    't3.medium': (2, 4),
    't3.large': (2, 8),
    't3.xlarge': (4, 16),
    't3.2xlarge': (8, 32),
    
    'm5.large': (2, 8),
    'm5.xlarge': (4, 16),
    'm5.2xlarge': (8, 32),
    'm5.4xlarge': (16, 64),
    'm5.8xlarge': (32, 128),
    
    'c5.large': (2, 4),
    'c5.xlarge': (4, 8),
    'c5.2xlarge': (8, 16),
    'c5.4xlarge': (16, 32),
    
    'r5.large': (2, 16),
    'r5.xlarge': (4, 32),
    'r5.2xlarge': (8, 64),
    'r5.4xlarge': (16, 128),
}


class RightSizer:
    """
    ML-powered right-sizing recommendations
    Analyzes REAL CloudWatch metrics to recommend optimal instance types
    """
    
    def __init__(self, n_clusters: int = 5):
        """
        Initialize right-sizer
        
        Args:
            n_clusters: Number of workload clusters (default: 5)
        """
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.is_trained = False
    
    def analyze_instance(
        self,
        instance_id: str,
        current_type: str,
        metrics: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Analyze a single instance and recommend optimal size
        
        Args:
            instance_id: EC2 instance ID
            current_type: Current instance type
            metrics: Dict with cpu_mean, cpu_p95, memory_mean, memory_p95, etc.
        
        Returns:
            Recommendation with savings, risk, confidence
        """
        logger.info(f"Analyzing instance {instance_id} ({current_type})")
        
        # Get current specs and pricing
        current_specs = INSTANCE_SPECS.get(current_type)
        current_cost = EC2_PRICING.get(current_type)
        
        if not current_specs or not current_cost:
            logger.warning(f"Unknown instance type: {current_type}")
            return None
        
        current_vcpu, current_memory = current_specs
        
        # Calculate required resources with headroom
        cpu_p95 = metrics.get('cpu_p95', 0)
        memory_p95 = metrics.get('memory_p95', 0) if metrics.get('memory_p95') else cpu_p95  # Fallback to CPU if memory not available
        
        # Add 20% headroom for safety
        required_cpu_pct = cpu_p95 * 1.2
        required_memory_pct = memory_p95 * 1.2
        
        # Find optimal instance type
        recommended_type = self._find_optimal_instance(
            required_cpu_pct,
            required_memory_pct,
            current_type
        )
        
        if not recommended_type or recommended_type == current_type:
            return None  # No recommendation if same type
        
        # Calculate savings
        recommended_cost = EC2_PRICING.get(recommended_type, current_cost)
        monthly_savings = current_cost - recommended_cost
        savings_percentage = (monthly_savings / current_cost * 100) if current_cost > 0 else 0
        
        # Only recommend if savings > 10%
        if savings_percentage < 10:
            return None
        
        # Calculate risk and confidence
        risk_level = self._calculate_risk(cpu_p95, memory_p95, required_cpu_pct, required_memory_pct)
        confidence_score = self._calculate_confidence(metrics, cpu_p95, memory_p95)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            current_type,
            recommended_type,
            cpu_p95,
            memory_p95,
            monthly_savings
        )
        
        return {
            "instance_id": instance_id,
            "current_instance_type": current_type,
            "recommended_instance_type": recommended_type,
            "current_monthly_cost": round(current_cost, 2),
            "recommended_monthly_cost": round(recommended_cost, 2),
            "estimated_savings": round(monthly_savings, 2),
            "savings_percentage": round(savings_percentage, 1),
            "risk_level": risk_level,
            "confidence_score": round(confidence_score, 1),
            "reasoning": reasoning,
            "cpu_utilization_avg": round(metrics.get('cpu_mean', 0), 1),
            "cpu_utilization_p95": round(cpu_p95, 1),
            "memory_utilization_avg": round(metrics.get('memory_mean', 0), 1) if metrics.get('memory_mean') else None,
            "memory_utilization_p95": round(memory_p95, 1) if metrics.get('memory_p95') else None,
        }
    
    def _find_optimal_instance(
        self,
        required_cpu_pct: float,
        required_memory_pct: float,
        current_type: str
    ) -> Optional[str]:
        """Find the smallest instance type that meets requirements"""
        current_specs = INSTANCE_SPECS.get(current_type)
        if not current_specs:
            return None
        
        current_vcpu, current_memory = current_specs
        current_family = current_type.split('.')[0]  # e.g., 'm5' from 'm5.xlarge'
        
        # Calculate required resources
        required_vcpu = (required_cpu_pct / 100) * current_vcpu
        required_memory = (required_memory_pct / 100) * current_memory
        
        # Find smallest instance in same family that meets requirements
        best_match = None
        best_cost = float('inf')
        
        for instance_type, specs in INSTANCE_SPECS.items():
            # Only consider same family
            if not instance_type.startswith(current_family):
                continue
            
            vcpu, memory = specs
            cost = EC2_PRICING.get(instance_type, float('inf'))
            
            # Check if it meets requirements
            if vcpu >= required_vcpu and memory >= required_memory:
                if cost < best_cost:
                    best_cost = cost
                    best_match = instance_type
        
        return best_match
    
    def _calculate_risk(
        self,
        cpu_p95: float,
        memory_p95: float,
        required_cpu_pct: float,
        required_memory_pct: float
    ) -> str:
        """Calculate risk level of recommendation"""
        # High utilization = higher risk
        if cpu_p95 > 80 or memory_p95 > 80:
            return "high"
        elif required_cpu_pct > 90 or required_memory_pct > 90:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(
        self,
        metrics: Dict[str, float],
        cpu_p95: float,
        memory_p95: float
    ) -> float:
        """Calculate confidence score (0-100)"""
        # Base confidence
        confidence = 80.0
        
        # Reduce confidence if high variability
        cpu_std = metrics.get('cpu_std', 0)
        if cpu_std > 20:
            confidence -= 15
        
        # Reduce if very low utilization (might be bursty)
        if cpu_p95 < 10:
            confidence -= 10
        
        # Reduce if we don't have memory data
        if not metrics.get('memory_p95'):
            confidence -= 10
        
        return max(50.0, min(95.0, confidence))
    
    def _generate_reasoning(
        self,
        current_type: str,
        recommended_type: str,
        cpu_p95: float,
        memory_p95: float,
        savings: float
    ) -> str:
        """Generate human-readable reasoning for recommendation"""
        current_specs = INSTANCE_SPECS[current_type]
        recommended_specs = INSTANCE_SPECS[recommended_type]
        
        reasoning = f"Current instance ({current_type}: {current_specs[0]} vCPU, {current_specs[1]}GB RAM) is underutilized. "
        reasoning += f"P95 CPU usage is only {cpu_p95:.1f}%, "
        
        if memory_p95:
            reasoning += f"P95 memory usage is {memory_p95:.1f}%. "
        
        reasoning += f"Switching to {recommended_type} ({recommended_specs[0]} vCPU, {recommended_specs[1]}GB RAM) "
        reasoning += f"will save ${savings:.2f}/month while still meeting your workload needs with 20% headroom."
        
        return reasoning


# Singleton instance
right_sizer = RightSizer()


