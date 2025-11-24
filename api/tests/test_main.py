"""
Test cases for the AWS Cost Optimizer API
"""

import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_api_title():
    """Test that the API has the correct title"""
    response = client.get("/docs")
    assert response.status_code == 200
    # The docs endpoint should return HTML content
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema():
    """Test that the OpenAPI schema is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "Multi-Cloud Cost Optimizer API"
    assert "paths" in data
    assert "/healthz" in data["paths"]
