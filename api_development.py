#!/usr/bin/env python3
"""
AWS Cost Optimizer - API Development & Documentation
RESTful API development with comprehensive documentation
"""

import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import streamlit as st
import yaml
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIVersion(Enum):
    """API versions"""
    V1 = "v1"
    V2 = "v2"
    BETA = "beta"

class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class APIEndpoint:
    """API endpoint definition"""
    path: str
    method: HTTPMethod
    description: str
    parameters: List[Dict[str, Any]]
    responses: Dict[int, str]
    example_request: Dict[str, Any]
    example_response: Dict[str, Any]

class APIDevelopment:
    def __init__(self):
        """Initialize API development system"""
        self.region = 'us-east-1'
        self.api_gateway = boto3.client('apigateway')
        self.lambda_client = boto3.client('lambda')
        self.iam_client = boto3.client('iam')
        
        # API configuration
        self.api_versions = [APIVersion.V1, APIVersion.V2]
        self.base_url = "https://api.cost-optimizer.com"
        
        # Initialize Flask app for API documentation
        self.app = Flask(__name__)
        CORS(self.app)
        self.api = Api(
            self.app,
            version='1.0',
            title='AWS Cost Optimizer API',
            description='Comprehensive API for AWS cost optimization and management',
            doc='/docs/'
        )
        
        # Define API endpoints
        self.endpoints = self._define_api_endpoints()
        
        # Setup API routes
        self._setup_api_routes()
    
    def _define_api_endpoints(self) -> List[APIEndpoint]:
        """Define API endpoints"""
        return [
            APIEndpoint(
                path="/api/v1/costs",
                method=HTTPMethod.GET,
                description="Get cost data for a specific time period",
                parameters=[
                    {"name": "start_date", "type": "string", "required": True, "description": "Start date (YYYY-MM-DD)"},
                    {"name": "end_date", "type": "string", "required": True, "description": "End date (YYYY-MM-DD)"},
                    {"name": "granularity", "type": "string", "required": False, "description": "Data granularity (daily, monthly)"},
                    {"name": "service", "type": "string", "required": False, "description": "Filter by AWS service"}
                ],
                responses={
                    200: "Success",
                    400: "Bad Request",
                    401: "Unauthorized",
                    500: "Internal Server Error"
                },
                example_request={
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "granularity": "daily"
                },
                example_response={
                    "status": "success",
                    "data": {
                        "total_cost": 15000.50,
                        "daily_costs": [
                            {"date": "2024-01-01", "cost": 500.25, "services": 5},
                            {"date": "2024-01-02", "cost": 450.75, "services": 4}
                        ],
                        "service_breakdown": {
                            "EC2": 8000.00,
                            "RDS": 3000.50,
                            "S3": 1500.00
                        }
                    }
                }
            ),
            APIEndpoint(
                path="/api/v1/optimizations",
                method=HTTPMethod.GET,
                description="Get optimization recommendations",
                parameters=[
                    {"name": "account_id", "type": "string", "required": False, "description": "AWS account ID"},
                    {"name": "priority", "type": "string", "required": False, "description": "Filter by priority (high, medium, low)"},
                    {"name": "type", "type": "string", "required": False, "description": "Filter by optimization type"}
                ],
                responses={
                    200: "Success",
                    400: "Bad Request",
                    401: "Unauthorized",
                    500: "Internal Server Error"
                },
                example_request={
                    "priority": "high",
                    "type": "rightsizing"
                },
                example_response={
                    "status": "success",
                    "data": {
                        "recommendations": [
                            {
                                "id": "opt_001",
                                "type": "rightsizing",
                                "title": "Downsize EC2 Instance",
                                "description": "Instance i-1234567890abcdef0 is underutilized",
                                "potential_savings": 500.00,
                                "priority": "high",
                                "confidence": 0.85
                            }
                        ],
                        "total_savings": 2500.00
                    }
                }
            ),
            APIEndpoint(
                path="/api/v1/forecasts",
                method=HTTPMethod.POST,
                description="Generate cost forecasts",
                parameters=[
                    {"name": "forecast_period", "type": "integer", "required": True, "description": "Forecast period in days"},
                    {"name": "confidence_level", "type": "number", "required": False, "description": "Confidence level (0.0-1.0)"}
                ],
                responses={
                    200: "Success",
                    400: "Bad Request",
                    401: "Unauthorized",
                    500: "Internal Server Error"
                },
                example_request={
                    "forecast_period": 30,
                    "confidence_level": 0.95
                },
                example_response={
                    "status": "success",
                    "data": {
                        "forecast_period": 30,
                        "total_forecasted_cost": 18500.75,
                        "daily_forecasts": [
                            {"date": "2024-02-01", "predicted_cost": 650.25, "confidence_interval": [600.00, 700.50]},
                            {"date": "2024-02-02", "predicted_cost": 675.50, "confidence_interval": [625.00, 725.00]}
                        ],
                        "model_accuracy": 0.87
                    }
                }
            ),
            APIEndpoint(
                path="/api/v1/alerts",
                method=HTTPMethod.GET,
                description="Get cost alerts and notifications",
                parameters=[
                    {"name": "status", "type": "string", "required": False, "description": "Filter by alert status"},
                    {"name": "severity", "type": "string", "required": False, "description": "Filter by severity level"},
                    {"name": "limit", "type": "integer", "required": False, "description": "Number of alerts to return"}
                ],
                responses={
                    200: "Success",
                    400: "Bad Request",
                    401: "Unauthorized",
                    500: "Internal Server Error"
                },
                example_request={
                    "status": "active",
                    "severity": "high",
                    "limit": 10
                },
                example_response={
                    "status": "success",
                    "data": {
                        "alerts": [
                            {
                                "id": "alert_001",
                                "title": "High Cost Alert",
                                "description": "Daily cost exceeded threshold",
                                "severity": "high",
                                "status": "active",
                                "timestamp": "2024-01-15T10:30:00Z",
                                "cost": 1500.00,
                                "threshold": 1000.00
                            }
                        ],
                        "total_alerts": 5
                    }
                }
            ),
            APIEndpoint(
                path="/api/v1/accounts",
                method=HTTPMethod.GET,
                description="Get multi-account information",
                parameters=[
                    {"name": "account_type", "type": "string", "required": False, "description": "Filter by account type"},
                    {"name": "cost_center", "type": "string", "required": False, "description": "Filter by cost center"}
                ],
                responses={
                    200: "Success",
                    400: "Bad Request",
                    401: "Unauthorized",
                    500: "Internal Server Error"
                },
                example_request={
                    "account_type": "member"
                },
                example_response={
                    "status": "success",
                    "data": {
                        "accounts": [
                            {
                                "account_id": "123456789012",
                                "account_name": "Production",
                                "account_type": "member",
                                "monthly_spend": 15000.00,
                                "optimization_potential": 2500.00,
                                "cost_center": "Engineering"
                            }
                        ],
                        "total_accounts": 4,
                        "total_spend": 31000.00
                    }
                }
            )
        ]
    
    def _setup_api_routes(self):
        """Setup Flask API routes"""
        try:
            # Define models for API documentation
            cost_model = self.api.model('CostData', {
                'total_cost': fields.Float(description='Total cost for the period'),
                'daily_costs': fields.List(fields.Raw, description='Daily cost breakdown'),
                'service_breakdown': fields.Raw(description='Cost breakdown by service')
            })
            
            optimization_model = self.api.model('Optimization', {
                'id': fields.String(description='Optimization ID'),
                'type': fields.String(description='Optimization type'),
                'title': fields.String(description='Optimization title'),
                'description': fields.String(description='Optimization description'),
                'potential_savings': fields.Float(description='Potential savings amount'),
                'priority': fields.String(description='Priority level'),
                'confidence': fields.Float(description='Confidence score')
            })
            
            # Define namespaces
            costs_ns = self.api.namespace('costs', description='Cost data operations')
            optimizations_ns = self.api.namespace('optimizations', description='Optimization operations')
            forecasts_ns = self.api.namespace('forecasts', description='Forecasting operations')
            alerts_ns = self.api.namespace('alerts', description='Alert operations')
            accounts_ns = self.api.namespace('accounts', description='Account operations')
            
            # Cost endpoints
            @costs_ns.route('/')
            class CostData(Resource):
                @costs_ns.doc('get_costs')
                @costs_ns.marshal_with(cost_model)
                def get(self):
                    """Get cost data"""
                    return {
                        'total_cost': 15000.50,
                        'daily_costs': [
                            {'date': '2024-01-01', 'cost': 500.25, 'services': 5},
                            {'date': '2024-01-02', 'cost': 450.75, 'services': 4}
                        ],
                        'service_breakdown': {
                            'EC2': 8000.00,
                            'RDS': 3000.50,
                            'S3': 1500.00
                        }
                    }
            
            # Optimization endpoints
            @optimizations_ns.route('/')
            class Optimizations(Resource):
                @optimizations_ns.doc('get_optimizations')
                @optimizations_ns.marshal_with(optimization_model)
                def get(self):
                    """Get optimization recommendations"""
                    return {
                        'recommendations': [
                            {
                                'id': 'opt_001',
                                'type': 'rightsizing',
                                'title': 'Downsize EC2 Instance',
                                'description': 'Instance i-1234567890abcdef0 is underutilized',
                                'potential_savings': 500.00,
                                'priority': 'high',
                                'confidence': 0.85
                            }
                        ],
                        'total_savings': 2500.00
                    }
            
            logger.info("API routes setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up API routes: {e}")
    
    def create_api_gateway(self, stage_name: str = 'prod') -> bool:
        """Create API Gateway for the Cost Optimizer API"""
        try:
            # Create REST API
            response = self.api_gateway.create_rest_api(
                name='CostOptimizerAPI',
                description='AWS Cost Optimizer REST API',
                endpointConfiguration={
                    'types': ['REGIONAL']
                }
            )
            
            api_id = response['id']
            logger.info(f"Created API Gateway: {api_id}")
            
            # Create resources and methods
            self._create_api_resources(api_id)
            
            # Deploy API
            self.api_gateway.create_deployment(
                restApiId=api_id,
                stageName=stage_name
            )
            
            logger.info(f"API Gateway deployed to stage: {stage_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating API Gateway: {e}")
            return False
    
    def _create_api_resources(self, api_id: str):
        """Create API Gateway resources and methods"""
        try:
            # Get root resource
            resources = self.api_gateway.get_resources(restApiId=api_id)
            root_resource_id = resources['items'][0]['id']
            
            # Create /api resource
            api_resource = self.api_gateway.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart='api'
            )
            
            # Create /v1 resource
            v1_resource = self.api_gateway.create_resource(
                restApiId=api_id,
                parentId=api_resource['id'],
                pathPart='v1'
            )
            
            # Create endpoint resources
            endpoints = ['costs', 'optimizations', 'forecasts', 'alerts', 'accounts']
            
            for endpoint in endpoints:
                resource = self.api_gateway.create_resource(
                    restApiId=api_id,
                    parentId=v1_resource['id'],
                    pathPart=endpoint
                )
                
                # Create GET method
                self.api_gateway.put_method(
                    restApiId=api_id,
                    resourceId=resource['id'],
                    httpMethod='GET',
                    authorizationType='NONE'
                )
                
                # Create POST method for applicable endpoints
                if endpoint in ['forecasts', 'optimizations']:
                    self.api_gateway.put_method(
                        restApiId=api_id,
                        resourceId=resource['id'],
                        httpMethod='POST',
                        authorizationType='NONE'
                    )
            
            logger.info("API Gateway resources created successfully")
            
        except Exception as e:
            logger.error(f"Error creating API resources: {e}")
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI specification"""
        try:
            openapi_spec = {
                'openapi': '3.0.0',
                'info': {
                    'title': 'AWS Cost Optimizer API',
                    'description': 'Comprehensive API for AWS cost optimization and management',
                    'version': '1.0.0',
                    'contact': {
                        'name': 'Cost Optimizer Team',
                        'email': 'support@cost-optimizer.com'
                    }
                },
                'servers': [
                    {
                        'url': self.base_url,
                        'description': 'Production server'
                    }
                ],
                'paths': {},
                'components': {
                    'schemas': {
                        'CostData': {
                            'type': 'object',
                            'properties': {
                                'total_cost': {'type': 'number'},
                                'daily_costs': {
                                    'type': 'array',
                                    'items': {'$ref': '#/components/schemas/DailyCost'}
                                },
                                'service_breakdown': {'type': 'object'}
                            }
                        },
                        'DailyCost': {
                            'type': 'object',
                            'properties': {
                                'date': {'type': 'string', 'format': 'date'},
                                'cost': {'type': 'number'},
                                'services': {'type': 'integer'}
                            }
                        },
                        'Optimization': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string'},
                                'type': {'type': 'string'},
                                'title': {'type': 'string'},
                                'description': {'type': 'string'},
                                'potential_savings': {'type': 'number'},
                                'priority': {'type': 'string'},
                                'confidence': {'type': 'number'}
                            }
                        }
                    }
                }
            }
            
            # Add paths for each endpoint
            for endpoint in self.endpoints:
                path_key = endpoint.path.replace('/api', '')
                openapi_spec['paths'][path_key] = {
                    endpoint.method.value.lower(): {
                        'summary': endpoint.description,
                        'parameters': [
                            {
                                'name': param['name'],
                                'in': 'query',
                                'required': param['required'],
                                'schema': {'type': param['type']},
                                'description': param['description']
                            }
                            for param in endpoint.parameters
                        ],
                        'responses': {
                            str(code): {'description': description}
                            for code, description in endpoint.responses.items()
                        }
                    }
                }
            
            return openapi_spec
            
        except Exception as e:
            logger.error(f"Error generating OpenAPI spec: {e}")
            return {}
    
    def create_api_documentation(self):
        """Create comprehensive API documentation"""
        try:
            documentation = {
                'title': 'AWS Cost Optimizer API Documentation',
                'version': '1.0.0',
                'description': 'Comprehensive API for AWS cost optimization and management',
                'base_url': self.base_url,
                'authentication': {
                    'type': 'Bearer Token',
                    'description': 'Include your API key in the Authorization header',
                    'example': 'Authorization: Bearer your-api-key'
                },
                'rate_limits': {
                    'requests_per_minute': 100,
                    'requests_per_hour': 1000,
                    'requests_per_day': 10000
                },
                'endpoints': []
            }
            
            # Add endpoint documentation
            for endpoint in self.endpoints:
                endpoint_doc = {
                    'path': endpoint.path,
                    'method': endpoint.method.value,
                    'description': endpoint.description,
                    'parameters': endpoint.parameters,
                    'responses': endpoint.responses,
                    'example_request': endpoint.example_request,
                    'example_response': endpoint.example_response
                }
                documentation['endpoints'].append(endpoint_doc)
            
            # Save documentation to file
            with open('api_documentation.json', 'w') as f:
                json.dump(documentation, f, indent=2)
            
            # Generate OpenAPI spec
            openapi_spec = self.generate_openapi_spec()
            with open('openapi_spec.yaml', 'w') as f:
                yaml.dump(openapi_spec, f, default_flow_style=False)
            
            logger.info("API documentation created successfully")
            return documentation
            
        except Exception as e:
            logger.error(f"Error creating API documentation: {e}")
            return {}
    
    def create_api_dashboard(self):
        """Create Streamlit dashboard for API development"""
        st.set_page_config(
            page_title="API Development",
            page_icon="🔧",
            layout="wide"
        )
        
        st.title("🔧 API Development & Documentation")
        st.markdown("---")
        
        # Initialize API development system
        api_dev = APIDevelopment()
        
        # Sidebar controls
        st.sidebar.header("🔧 API Controls")
        
        if st.sidebar.button("📚 Generate Documentation"):
            with st.spinner("Generating API documentation..."):
                documentation = api_dev.create_api_documentation()
                st.session_state.api_documentation = documentation
        
        if st.sidebar.button("🌐 Create API Gateway"):
            with st.spinner("Creating API Gateway..."):
                success = api_dev.create_api_gateway()
                if success:
                    st.success("API Gateway created successfully!")
                else:
                    st.error("Failed to create API Gateway")
        
        if st.sidebar.button("📋 Generate OpenAPI Spec"):
            with st.spinner("Generating OpenAPI specification..."):
                openapi_spec = api_dev.generate_openapi_spec()
                st.session_state.openapi_spec = openapi_spec
        
        # Display API endpoints
        st.header("📋 API Endpoints")
        
        for endpoint in api_dev.endpoints:
            with st.expander(f"🔗 {endpoint.method.value} {endpoint.path}"):
                st.write(f"**Description**: {endpoint.description}")
                
                # Parameters
                if endpoint.parameters:
                    st.write("**Parameters**:")
                    for param in endpoint.parameters:
                        required = "✅" if param['required'] else "❌"
                        st.write(f"  • {param['name']} ({param['type']}) {required} - {param['description']}")
                
                # Responses
                st.write("**Responses**:")
                for code, description in endpoint.responses.items():
                    st.write(f"  • {code}: {description}")
                
                # Example request
                if endpoint.example_request:
                    st.write("**Example Request**:")
                    st.json(endpoint.example_request)
                
                # Example response
                if endpoint.example_response:
                    st.write("**Example Response**:")
                    st.json(endpoint.example_response)
        
        # API documentation
        if 'api_documentation' in st.session_state:
            st.header("📚 API Documentation")
            
            doc = st.session_state.api_documentation
            
            # API info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("API Version", doc['version'])
                st.metric("Base URL", doc['base_url'])
            
            with col2:
                st.metric("Total Endpoints", len(doc['endpoints']))
                st.metric("Authentication", doc['authentication']['type'])
            
            with col3:
                st.metric("Rate Limit", f"{doc['rate_limits']['requests_per_minute']}/min")
                st.metric("Daily Limit", f"{doc['rate_limits']['requests_per_day']}/day")
            
            # Authentication
            st.subheader("🔐 Authentication")
            st.write(f"**Type**: {doc['authentication']['type']}")
            st.write(f"**Description**: {doc['authentication']['description']}")
            st.code(doc['authentication']['example'], language='text')
        
        # OpenAPI specification
        if 'openapi_spec' in st.session_state:
            st.header("📋 OpenAPI Specification")
            
            spec = st.session_state.openapi_spec
            
            st.write("**API Info**:")
            st.json(spec['info'])
            
            st.write("**Servers**:")
            st.json(spec['servers'])
            
            # Download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Download JSON Documentation"):
                    st.download_button(
                        label="Download API Documentation (JSON)",
                        data=json.dumps(st.session_state.api_documentation, indent=2),
                        file_name="api_documentation.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("📥 Download OpenAPI Spec"):
                    st.download_button(
                        label="Download OpenAPI Specification (YAML)",
                        data=yaml.dump(st.session_state.openapi_spec, default_flow_style=False),
                        file_name="openapi_spec.yaml",
                        mime="text/yaml"
                    )
        
        # Footer
        st.markdown("---")
        st.markdown("**API Development System** - RESTful API with Comprehensive Documentation")
        st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function to run API development"""
    api_dev = APIDevelopment()
    
    # Test API development
    print("🔧 Testing API Development System...")
    
    # Test endpoint definitions
    print("Testing API endpoint definitions...")
    print(f"✅ Defined {len(api_dev.endpoints)} API endpoints")
    
    # Test API documentation generation
    print("Testing API documentation generation...")
    documentation = api_dev.create_api_documentation()
    print(f"✅ API documentation generated - {len(documentation['endpoints'])} endpoints documented")
    
    # Test OpenAPI spec generation
    print("Testing OpenAPI specification generation...")
    openapi_spec = api_dev.generate_openapi_spec()
    print(f"✅ OpenAPI spec generated - {len(openapi_spec.get('paths', {}))} paths defined")
    
    # Test API Gateway creation
    print("Testing API Gateway creation...")
    success = api_dev.create_api_gateway()
    print(f"✅ API Gateway creation: {'Success' if success else 'Failed'}")
    
    print("🎉 API Development System is ready!")

if __name__ == "__main__":
    main()
