#!/usr/bin/env python3
"""
AWS Cost Optimizer - Third-Party Integrations
Integration with external services and platforms
"""

import boto3
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Integration types"""
    SLACK = "slack"
    TEAMS = "teams"
    JIRA = "jira"
    SERVICENOW = "servicenow"
    SALESFORCE = "salesforce"
    ZENDESK = "zendesk"
    PAGERDUTY = "pagerduty"
    DATADOG = "datadog"
    NEWRELIC = "newrelic"
    SPLUNK = "splunk"

class IntegrationStatus(Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"

@dataclass
class IntegrationConfig:
    """Integration configuration"""
    name: str
    type: IntegrationType
    status: IntegrationStatus
    webhook_url: str
    api_key: str
    enabled: bool
    settings: Dict[str, Any]

class ThirdPartyIntegrations:
    def __init__(self):
        """Initialize third-party integrations system"""
        self.region = 'us-east-1'
        self.sns_client = boto3.client('sns')
        self.ses_client = boto3.client('ses')
        self.secrets_manager = boto3.client('secretsmanager')
        
        # Integration configurations
        self.integrations = self._load_integration_configs()
        
        # API endpoints for external services
        self.api_endpoints = {
            'slack': 'https://hooks.slack.com/services',
            'teams': 'https://outlook.office.com/webhook',
            'jira': 'https://your-domain.atlassian.net/rest/api/3',
            'servicenow': 'https://your-instance.service-now.com/api/now/table',
            'salesforce': 'https://your-domain.salesforce.com/services/data/v52.0',
            'zendesk': 'https://your-domain.zendesk.com/api/v2',
            'pagerduty': 'https://api.pagerduty.com',
            'datadog': 'https://api.datadoghq.com/api/v1',
            'newrelic': 'https://api.newrelic.com/v2',
            'splunk': 'https://your-splunk-instance.com/servicesNS'
        }
    
    def _load_integration_configs(self) -> Dict[str, IntegrationConfig]:
        """Load integration configurations"""
        return {
            'slack': IntegrationConfig(
                name='Slack Notifications',
                type=IntegrationType.SLACK,
                status=IntegrationStatus.ACTIVE,
                webhook_url='https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK_URL',
                api_key='xoxb-your-slack-bot-token',
                enabled=True,
                settings={
                    'channel': '#cost-optimization',
                    'username': 'Cost Optimizer Bot',
                    'icon_emoji': ':money_with_wings:'
                }
            ),
            'teams': IntegrationConfig(
                name='Microsoft Teams',
                type=IntegrationType.TEAMS,
                status=IntegrationStatus.ACTIVE,
                webhook_url='https://outlook.office.com/webhook/your-teams-webhook',
                api_key='',
                enabled=True,
                settings={
                    'title': 'Cost Optimization Alert',
                    'theme_color': '0078D4'
                }
            ),
            'jira': IntegrationConfig(
                name='JIRA Integration',
                type=IntegrationType.JIRA,
                status=IntegrationStatus.ACTIVE,
                webhook_url='',
                api_key='your-jira-api-token',
                enabled=True,
                settings={
                    'project_key': 'COST',
                    'issue_type': 'Task',
                    'priority': 'Medium'
                }
            ),
            'pagerduty': IntegrationConfig(
                name='PagerDuty Alerts',
                type=IntegrationType.PAGERDUTY,
                status=IntegrationStatus.ACTIVE,
                webhook_url='',
                api_key='your-pagerduty-api-key',
                enabled=True,
                settings={
                    'service_key': 'your-pagerduty-service-key',
                    'severity': 'critical'
                }
            ),
            'datadog': IntegrationConfig(
                name='Datadog Metrics',
                type=IntegrationType.DATADOG,
                status=IntegrationStatus.ACTIVE,
                webhook_url='',
                api_key='your-datadog-api-key',
                enabled=True,
                settings={
                    'app_key': 'your-datadog-app-key',
                    'metric_prefix': 'cost_optimizer'
                }
            )
        }
    
    def send_slack_notification(self, message: str, channel: str = None) -> bool:
        """Send notification to Slack"""
        try:
            config = self.integrations['slack']
            
            if not config.enabled:
                logger.info("Slack integration is disabled")
                return True
            
            payload = {
                'text': message,
                'channel': channel or config.settings['channel'],
                'username': config.settings['username'],
                'icon_emoji': config.settings['icon_emoji']
            }
            
            response = requests.post(
                config.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def send_teams_notification(self, title: str, message: str) -> bool:
        """Send notification to Microsoft Teams"""
        try:
            config = self.integrations['teams']
            
            if not config.enabled:
                logger.info("Teams integration is disabled")
                return True
            
            payload = {
                '@type': 'MessageCard',
                '@context': 'http://schema.org/extensions',
                'themeColor': config.settings['theme_color'],
                'summary': title,
                'sections': [{
                    'activityTitle': title,
                    'activitySubtitle': 'Cost Optimization Alert',
                    'activityImage': 'https://img.icons8.com/color/48/000000/amazon-web-services.png',
                    'text': message,
                    'markdown': True
                }]
            }
            
            response = requests.post(
                config.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Teams notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send Teams notification: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Teams notification: {e}")
            return False
    
    def create_jira_ticket(self, summary: str, description: str, priority: str = 'Medium') -> bool:
        """Create JIRA ticket for cost optimization"""
        try:
            config = self.integrations['jira']
            
            if not config.enabled:
                logger.info("JIRA integration is disabled")
                return True
            
            headers = {
                'Authorization': f'Basic {config.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'fields': {
                    'project': {'key': config.settings['project_key']},
                    'summary': summary,
                    'description': description,
                    'issuetype': {'name': config.settings['issue_type']},
                    'priority': {'name': priority}
                }
            }
            
            response = requests.post(
                f"{self.api_endpoints['jira']}/issue",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                ticket_data = response.json()
                logger.info(f"JIRA ticket created: {ticket_data['key']}")
                return True
            else:
                logger.error(f"Failed to create JIRA ticket: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating JIRA ticket: {e}")
            return False
    
    def send_pagerduty_alert(self, title: str, description: str, severity: str = 'critical') -> bool:
        """Send alert to PagerDuty"""
        try:
            config = self.integrations['pagerduty']
            
            if not config.enabled:
                logger.info("PagerDuty integration is disabled")
                return True
            
            headers = {
                'Authorization': f'Token token={config.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'routing_key': config.settings['service_key'],
                'event_action': 'trigger',
                'dedup_key': f'cost-optimizer-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'payload': {
                    'summary': title,
                    'source': 'Cost Optimizer',
                    'severity': severity,
                    'custom_details': {
                        'description': description,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            }
            
            response = requests.post(
                f"{self.api_endpoints['pagerduty']}/v2/enqueue",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 202:
                logger.info("PagerDuty alert sent successfully")
                return True
            else:
                logger.error(f"Failed to send PagerDuty alert: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending PagerDuty alert: {e}")
            return False
    
    def send_datadog_metric(self, metric_name: str, value: float, tags: List[str] = None) -> bool:
        """Send metric to Datadog"""
        try:
            config = self.integrations['datadog']
            
            if not config.enabled:
                logger.info("Datadog integration is disabled")
                return True
            
            headers = {
                'DD-API-KEY': config.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'series': [{
                    'metric': f"{config.settings['metric_prefix']}.{metric_name}",
                    'points': [[int(datetime.now().timestamp()), value]],
                    'type': 'gauge',
                    'tags': tags or ['service:cost-optimizer']
                }]
            }
            
            response = requests.post(
                f"{self.api_endpoints['datadog']}/series",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 202:
                logger.info(f"Datadog metric sent: {metric_name}")
                return True
            else:
                logger.error(f"Failed to send Datadog metric: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Datadog metric: {e}")
            return False
    
    def test_integration(self, integration_name: str) -> Dict[str, Any]:
        """Test integration connectivity"""
        try:
            config = self.integrations[integration_name]
            
            test_results = {
                'integration': integration_name,
                'status': 'unknown',
                'response_time': 0,
                'error': None,
                'timestamp': datetime.now().isoformat()
            }
            
            start_time = datetime.now()
            
            if integration_name == 'slack':
                success = self.send_slack_notification("🧪 Test notification from Cost Optimizer")
            elif integration_name == 'teams':
                success = self.send_teams_notification("Test Alert", "This is a test notification from Cost Optimizer")
            elif integration_name == 'jira':
                success = self.create_jira_ticket("Test Ticket", "This is a test ticket from Cost Optimizer")
            elif integration_name == 'pagerduty':
                success = self.send_pagerduty_alert("Test Alert", "This is a test alert from Cost Optimizer")
            elif integration_name == 'datadog':
                success = self.send_datadog_metric("test.metric", 1.0, ['test:true'])
            else:
                success = False
                test_results['error'] = f"Unknown integration: {integration_name}"
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            test_results['status'] = 'success' if success else 'failed'
            test_results['response_time'] = response_time
            
            return test_results
            
        except Exception as e:
            logger.error(f"Error testing integration {integration_name}: {e}")
            return {
                'integration': integration_name,
                'status': 'error',
                'response_time': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        try:
            status = {
                'total_integrations': len(self.integrations),
                'active_integrations': 0,
                'inactive_integrations': 0,
                'error_integrations': 0,
                'integrations': []
            }
            
            for name, config in self.integrations.items():
                integration_status = {
                    'name': name,
                    'type': config.type.value,
                    'status': config.status.value,
                    'enabled': config.enabled,
                    'last_checked': datetime.now().isoformat()
                }
                
                status['integrations'].append(integration_status)
                
                if config.status == IntegrationStatus.ACTIVE:
                    status['active_integrations'] += 1
                elif config.status == IntegrationStatus.INACTIVE:
                    status['inactive_integrations'] += 1
                elif config.status == IntegrationStatus.ERROR:
                    status['error_integrations'] += 1
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting integration status: {e}")
            return {}
    
    def create_integrations_dashboard(self):
        """Create Streamlit dashboard for third-party integrations"""
        st.set_page_config(
            page_title="Third-Party Integrations",
            page_icon="🔗",
            layout="wide"
        )
        
        st.title("🔗 Third-Party Integrations")
        st.markdown("---")
        
        # Initialize integrations system
        integrations = ThirdPartyIntegrations()
        
        # Sidebar controls
        st.sidebar.header("🔗 Integration Controls")
        
        if st.sidebar.button("📊 Check Integration Status"):
            with st.spinner("Checking integration status..."):
                status = integrations.get_integration_status()
                st.session_state.integration_status = status
        
        if st.sidebar.button("🧪 Test All Integrations"):
            with st.spinner("Testing all integrations..."):
                test_results = []
                for integration_name in integrations.integrations.keys():
                    result = integrations.test_integration(integration_name)
                    test_results.append(result)
                st.session_state.test_results = test_results
        
        # Display integration status
        if 'integration_status' in st.session_state:
            status = st.session_state.integration_status
            
            st.header("📊 Integration Status")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Integrations",
                    status['total_integrations'],
                    delta="configured"
                )
            
            with col2:
                st.metric(
                    "Active",
                    status['active_integrations'],
                    delta="working"
                )
            
            with col3:
                st.metric(
                    "Inactive",
                    status['inactive_integrations'],
                    delta="disabled"
                )
            
            with col4:
                st.metric(
                    "Errors",
                    status['error_integrations'],
                    delta="issues"
                )
            
            # Integration details
            st.subheader("Integration Details")
            
            for integration in status['integrations']:
                status_color = {
                    'active': '🟢',
                    'inactive': '🟡',
                    'error': '🔴',
                    'pending': '🟠'
                }
                
                with st.expander(f"{status_color[integration['status']]} {integration['name']} - {integration['type'].title()}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Status**: {integration['status'].title()}")
                        st.write(f"**Type**: {integration['type'].title()}")
                        st.write(f"**Enabled**: {'✅' if integration['enabled'] else '❌'}")
                    
                    with col2:
                        st.write(f"**Last Checked**: {integration['last_checked']}")
                        
                        # Test button for individual integration
                        if st.button(f"Test {integration['name']}", key=f"test_{integration['name']}"):
                            with st.spinner(f"Testing {integration['name']}..."):
                                result = integrations.test_integration(integration['name'])
                                if result['status'] == 'success':
                                    st.success(f"✅ {integration['name']} test successful!")
                                else:
                                    st.error(f"❌ {integration['name']} test failed: {result.get('error', 'Unknown error')}")
        
        # Test results
        if 'test_results' in st.session_state:
            st.header("🧪 Test Results")
            
            test_results = st.session_state.test_results
            
            # Test results table
            df = pd.DataFrame(test_results)
            
            # Status distribution
            status_counts = df['status'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Test Results Summary")
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Integration Test Results"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Response Times")
                fig = px.bar(
                    df,
                    x='integration',
                    y='response_time',
                    title="Integration Response Times",
                    labels={'response_time': 'Response Time (seconds)', 'integration': 'Integration'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed results
            st.subheader("Detailed Test Results")
            
            for result in test_results:
                status_icon = "✅" if result['status'] == 'success' else "❌"
                
                with st.expander(f"{status_icon} {result['integration']} - {result['status'].title()}"):
                    st.write(f"**Response Time**: {result['response_time']:.2f} seconds")
                    st.write(f"**Timestamp**: {result['timestamp']}")
                    
                    if result.get('error'):
                        st.error(f"**Error**: {result['error']}")
        
        # Integration examples
        st.header("📝 Integration Examples")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Slack Notification")
            if st.button("Send Test Slack Message"):
                success = integrations.send_slack_notification("🧪 Test message from Cost Optimizer")
                if success:
                    st.success("Slack notification sent!")
                else:
                    st.error("Failed to send Slack notification")
        
        with col2:
            st.subheader("Teams Notification")
            if st.button("Send Test Teams Message"):
                success = integrations.send_teams_notification("Test Alert", "This is a test notification")
                if success:
                    st.success("Teams notification sent!")
                else:
                    st.error("Failed to send Teams notification")
        
        # Footer
        st.markdown("---")
        st.markdown("**Third-Party Integrations System** - External Service Connectivity")
        st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function to run third-party integrations"""
    integrations = ThirdPartyIntegrations()
    
    # Test integrations system
    print("🔗 Testing Third-Party Integrations System...")
    
    # Test integration configurations
    print("Testing integration configurations...")
    for name, config in integrations.integrations.items():
        print(f"✅ {name}: {config.status.value} - {config.type.value}")
    
    # Test integration status
    print("Testing integration status...")
    status = integrations.get_integration_status()
    print(f"✅ Integration status - {status['active_integrations']} active, {status['inactive_integrations']} inactive")
    
    # Test individual integrations
    print("Testing individual integrations...")
    for integration_name in ['slack', 'teams', 'jira', 'pagerduty', 'datadog']:
        result = integrations.test_integration(integration_name)
        print(f"✅ {integration_name}: {result['status']} ({result['response_time']:.2f}s)")
    
    print("🎉 Third-Party Integrations System is ready!")

if __name__ == "__main__":
    main()
