"""
Unit tests for AWS Cost Service
Tests the business logic for cost data processing, alerts, and recommendations
"""

import pytest
from unittest.mock import Mock, patch
from api.services.aws_cost_service import AWSCostService, aws_cost_service


class TestAWSCostService:
    """Test suite for AWSCostService"""
    
    def setup_method(self):
        """Setup for each test"""
        self.service = AWSCostService()
    
    def test_process_service_costs_basic(self):
        """Test processing service costs from Athena results"""
        service_rows = [
            {"service": "Amazon EC2", "cost": "100.50"},
            {"service": "Amazon S3", "cost": "50.25"},
            {"service": "AWS Lambda", "cost": "25.00"},
        ]
        
        result = self.service._process_service_costs(service_rows)
        
        assert len(result) == 3
        assert result[0]["name"] == "EC2"
        assert result[0]["cost"] == 100.50
        assert result[0]["percentage"] > 0
        assert "trend" in result[0]
    
    def test_process_service_costs_filters_zero_costs(self):
        """Test that zero/negative costs are filtered out"""
        service_rows = [
            {"service": "Amazon EC2", "cost": "100.00"},
            {"service": "Amazon S3", "cost": "0"},
            {"service": "AWS Lambda", "cost": "-10.00"},
        ]
        
        result = self.service._process_service_costs(service_rows)
        
        assert len(result) == 1
        assert result[0]["name"] == "EC2"
    
    def test_process_daily_costs(self):
        """Test processing daily cost data"""
        daily_rows = [
            {"day": "2024-11-01", "cost": "100.00"},
            {"day": "2024-11-02", "cost": "150.50"},
            {"day": "2024-11-03", "cost": "120.25"},
        ]
        
        result = self.service._process_daily_costs(daily_rows)
        
        assert len(result) == 3
        assert result[0]["date"] == "2024-11-01"
        assert result[0]["cost"] == 100.00
        assert result[1]["cost"] == 150.50
    
    def test_build_dynamic_alerts_cost_spike(self):
        """Test that cost spike alert is generated"""
        cost_summary = {
            "daily": [
                {"cost": 100.00},
                {"cost": 105.00},
                {"cost": 110.00},
                {"cost": 200.00},  # Spike!
            ],
            "total_cost": 515.00,
        }
        
        alerts = self.service.build_dynamic_alerts(cost_summary, {})
        
        # Should detect spike
        assert len(alerts) > 0
        spike_alerts = [a for a in alerts if a["id"] == "auto-cost-spike"]
        assert len(spike_alerts) == 1
        assert spike_alerts[0]["severity"] == "high"
    
    def test_build_dynamic_alerts_no_spike(self):
        """Test that no alert is generated for stable costs"""
        cost_summary = {
            "daily": [
                {"cost": 100.00},
                {"cost": 105.00},
                {"cost": 110.00},
                {"cost": 108.00},  # Stable
            ],
            "total_cost": 423.00,
        }
        
        alerts = self.service.build_dynamic_alerts(cost_summary, {})
        
        # Should not detect spike
        spike_alerts = [a for a in alerts if a["id"] == "auto-cost-spike"]
        assert len(spike_alerts) == 0
    
    def test_build_optimization_recommendations(self):
        """Test optimization recommendations generation"""
        cost_summary = {
            "services": [
                {"name": "EC2", "cost": 1000.00, "percentage": 50.0},
                {"name": "S3", "cost": 500.00, "percentage": 25.0},
                {"name": "Lambda", "cost": 200.00, "percentage": 10.0},
            ],
            "total_cost": 1700.00,
        }
        
        recommendations = self.service.build_optimization_recommendations(cost_summary, {})
        
        # Should generate recommendations
        assert len(recommendations) > 0
        
        # Check EC2 recommendation
        ec2_recs = [r for r in recommendations if r["service"] == "EC2"]
        assert len(ec2_recs) > 0
        assert ec2_recs[0]["potentialSavings"] > 0
    
    @patch('api.services.aws_cost_service.assume_vendor_role')
    @patch('api.services.aws_cost_service.run_athena_query')
    def test_fetch_tenant_cost_data(self, mock_query, mock_assume_role):
        """Test fetching tenant cost data (mocked)"""
        # Mock tenant
        mock_tenant = Mock()
        mock_tenant.aws_role_arn = "arn:aws:iam::123:role/test"
        mock_tenant.external_id = "test-external-id"
        mock_tenant.region = "us-east-1"
        mock_tenant.athena_workgroup = "primary"
        mock_tenant.athena_db = "test_db"
        mock_tenant.athena_table = "test_table"
        mock_tenant.id = 1
        
        # Mock AWS session
        mock_session = Mock()
        mock_assume_role.return_value = mock_session
        
        # Mock Athena query results
        mock_query.side_effect = [
            # Service costs
            [
                {"service": "Amazon EC2", "cost": "100.00"},
                {"service": "Amazon S3", "cost": "50.00"},
            ],
            # Daily costs
            [
                {"day": "2024-11-01", "cost": "75.00"},
                {"day": "2024-11-02", "cost": "75.00"},
            ],
        ]
        
        result = self.service.fetch_tenant_cost_data(mock_tenant, 7)
        
        # Verify results
        assert "services" in result
        assert "daily" in result
        assert "total_cost" in result
        assert "avg_daily" in result
        
        assert len(result["services"]) == 2
        assert len(result["daily"]) == 2
        assert result["total_cost"] == 150.00
        assert result["avg_daily"] == 75.00
        
        # Verify service was called
        mock_assume_role.assert_called_once()
        assert mock_query.call_count == 2


def test_singleton_instance():
    """Test that singleton instance is available"""
    assert aws_cost_service is not None
    assert isinstance(aws_cost_service, AWSCostService)


