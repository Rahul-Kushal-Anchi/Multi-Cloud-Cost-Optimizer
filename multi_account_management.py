#!/usr/bin/env python3
"""
AWS Cost Optimizer - Multi-Account Management System
Advanced multi-account cost management and cross-account optimization
"""

import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccountType(Enum):
    """Account types"""
    MASTER = "master"
    MEMBER = "member"
    STANDALONE = "standalone"

class AccountStatus(Enum):
    """Account status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    FAILED = "failed"

@dataclass
class AccountInfo:
    """Account information"""
    account_id: str
    account_name: str
    account_type: AccountType
    status: AccountStatus
    region: str
    cost_center: str
    owner: str
    tags: Dict[str, str]
    monthly_spend: float
    optimization_potential: float

class MultiAccountManager:
    def __init__(self):
        """Initialize multi-account management system"""
        self.region = 'us-east-1'
        self.organizations = boto3.client('organizations')
        self.ce_client = boto3.client('ce')
        self.sts_client = boto3.client('sts')
        self.iam_client = boto3.client('iam')
        
        # Account management
        self.accounts = {}
        self.cross_account_roles = {}
        
        # Load account configurations
        self._load_account_configurations()
    
    def _load_account_configurations(self):
        """Load account configurations"""
        # Simulate account data
        self.accounts = {
            '123456789012': AccountInfo(
                account_id='123456789012',
                account_name='Production',
                account_type=AccountType.MASTER,
                status=AccountStatus.ACTIVE,
                region='us-east-1',
                cost_center='Engineering',
                owner='engineering@company.com',
                tags={'Environment': 'Production', 'Team': 'Engineering'},
                monthly_spend=15000.0,
                optimization_potential=2500.0
            ),
            '234567890123': AccountInfo(
                account_id='234567890123',
                account_name='Development',
                account_type=AccountType.MEMBER,
                status=AccountStatus.ACTIVE,
                region='us-east-1',
                cost_center='Engineering',
                owner='dev-team@company.com',
                tags={'Environment': 'Development', 'Team': 'Engineering'},
                monthly_spend=5000.0,
                optimization_potential=800.0
            ),
            '345678901234': AccountInfo(
                account_id='345678901234',
                account_name='Staging',
                account_type=AccountType.MEMBER,
                status=AccountStatus.ACTIVE,
                region='us-east-1',
                cost_center='Engineering',
                owner='qa-team@company.com',
                tags={'Environment': 'Staging', 'Team': 'QA'},
                monthly_spend=3000.0,
                optimization_potential=500.0
            ),
            '456789012345': AccountInfo(
                account_id='456789012345',
                account_name='Analytics',
                account_type=AccountType.MEMBER,
                status=AccountStatus.ACTIVE,
                region='us-east-1',
                cost_center='Data',
                owner='data-team@company.com',
                tags={'Environment': 'Analytics', 'Team': 'Data'},
                monthly_spend=8000.0,
                optimization_potential=1200.0
            )
        }
    
    def get_all_accounts(self) -> List[AccountInfo]:
        """Get all managed accounts"""
        return list(self.accounts.values())
    
    def get_account_summary(self) -> Dict[str, Any]:
        """Get comprehensive account summary"""
        try:
            accounts = self.get_all_accounts()
            
            # Calculate totals
            total_accounts = len(accounts)
            total_monthly_spend = sum(acc.monthly_spend for acc in accounts)
            total_optimization_potential = sum(acc.optimization_potential for acc in accounts)
            
            # Account distribution by type
            account_types = {}
            for acc in accounts:
                acc_type = acc.account_type.value
                account_types[acc_type] = account_types.get(acc_type, 0) + 1
            
            # Cost center distribution
            cost_centers = {}
            for acc in accounts:
                cost_center = acc.cost_center
                if cost_center not in cost_centers:
                    cost_centers[cost_center] = {'spend': 0, 'accounts': 0}
                cost_centers[cost_center]['spend'] += acc.monthly_spend
                cost_centers[cost_center]['accounts'] += 1
            
            # Top spending accounts
            top_accounts = sorted(accounts, key=lambda x: x.monthly_spend, reverse=True)[:5]
            
            return {
                'total_accounts': total_accounts,
                'total_monthly_spend': total_monthly_spend,
                'total_optimization_potential': total_optimization_potential,
                'account_types': account_types,
                'cost_centers': cost_centers,
                'top_accounts': [
                    {
                        'account_id': acc.account_id,
                        'account_name': acc.account_name,
                        'monthly_spend': acc.monthly_spend,
                        'optimization_potential': acc.optimization_potential
                    }
                    for acc in top_accounts
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {}
    
    def get_cross_account_costs(self, account_id: str) -> Dict[str, Any]:
        """Get cost data for a specific account"""
        try:
            # Simulate cross-account cost data
            cost_data = {
                'account_id': account_id,
                'account_name': self.accounts[account_id].account_name,
                'monthly_spend': self.accounts[account_id].monthly_spend,
                'daily_costs': self._generate_daily_costs(30),
                'service_breakdown': self._generate_service_breakdown(),
                'region_breakdown': self._generate_region_breakdown(),
                'optimization_opportunities': self._generate_optimization_opportunities(account_id)
            }
            
            return cost_data
            
        except Exception as e:
            logger.error(f"Error getting cross-account costs: {e}")
            return {}
    
    def _generate_daily_costs(self, days: int) -> List[Dict[str, Any]]:
        """Generate daily cost data"""
        import random
        
        daily_costs = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            cost = random.uniform(100, 1000)
            
            daily_costs.append({
                'date': date.strftime('%Y-%m-%d'),
                'cost': round(cost, 2),
                'services': random.randint(5, 15),
                'regions': random.randint(2, 8)
            })
        
        return daily_costs
    
    def _generate_service_breakdown(self) -> List[Dict[str, Any]]:
        """Generate service cost breakdown"""
        services = [
            {'name': 'EC2', 'cost': 4500.0, 'percentage': 35.0},
            {'name': 'RDS', 'cost': 2800.0, 'percentage': 22.0},
            {'name': 'S3', 'cost': 1200.0, 'percentage': 9.0},
            {'name': 'Lambda', 'cost': 800.0, 'percentage': 6.0},
            {'name': 'CloudWatch', 'cost': 600.0, 'percentage': 5.0},
            {'name': 'ELB', 'cost': 500.0, 'percentage': 4.0},
            {'name': 'EBS', 'cost': 400.0, 'percentage': 3.0},
            {'name': 'Other', 'cost': 2200.0, 'percentage': 16.0}
        ]
        
        return services
    
    def _generate_region_breakdown(self) -> List[Dict[str, Any]]:
        """Generate region cost breakdown"""
        regions = [
            {'region': 'us-east-1', 'cost': 6500.0, 'percentage': 51.0},
            {'region': 'us-west-2', 'cost': 3200.0, 'percentage': 25.0},
            {'region': 'eu-west-1', 'cost': 1800.0, 'percentage': 14.0},
            {'region': 'ap-southeast-1', 'cost': 1200.0, 'percentage': 10.0}
        ]
        
        return regions
    
    def _generate_optimization_opportunities(self, account_id: str) -> List[Dict[str, Any]]:
        """Generate optimization opportunities for an account"""
        opportunities = [
            {
                'type': 'rightsizing',
                'title': 'EC2 Instance Rightsizing',
                'description': 'Downsize underutilized EC2 instances',
                'potential_savings': 1200.0,
                'effort': 'medium',
                'priority': 'high'
            },
            {
                'type': 'reserved_instances',
                'title': 'Purchase Reserved Instances',
                'description': 'Buy RIs for consistent workloads',
                'potential_savings': 800.0,
                'effort': 'low',
                'priority': 'medium'
            },
            {
                'type': 'storage_optimization',
                'title': 'S3 Storage Class Optimization',
                'description': 'Move infrequently accessed data to IA',
                'potential_savings': 300.0,
                'effort': 'low',
                'priority': 'low'
            }
        ]
        
        return opportunities
    
    def create_cross_account_role(self, target_account_id: str) -> bool:
        """Create cross-account access role"""
        try:
            role_name = f"CostOptimizerCrossAccountRole"
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": f"arn:aws:iam::123456789012:root"  # Master account
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "sts:ExternalId": "cost-optimizer-external-id"
                            }
                        }
                    }
                ]
            }
            
            # Create role
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"Cross-account role for Cost Optimizer access to {target_account_id}",
                Tags=[
                    {'Key': 'Project', 'Value': 'CostOptimizer'},
                    {'Key': 'TargetAccount', 'Value': target_account_id}
                ]
            )
            
            # Attach policies
            policies = [
                'arn:aws:iam::aws:policy/ReadOnlyAccess',
                'arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess'
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created cross-account role for {target_account_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating cross-account role: {e}")
            return False
    
    def get_consolidated_recommendations(self) -> List[Dict[str, Any]]:
        """Get consolidated optimization recommendations across all accounts"""
        try:
            recommendations = []
            
            for account_id, account_info in self.accounts.items():
                opportunities = self._generate_optimization_opportunities(account_id)
                
                for opp in opportunities:
                    recommendations.append({
                        'account_id': account_id,
                        'account_name': account_info.account_name,
                        'cost_center': account_info.cost_center,
                        'type': opp['type'],
                        'title': opp['title'],
                        'description': opp['description'],
                        'potential_savings': opp['potential_savings'],
                        'effort': opp['effort'],
                        'priority': opp['priority']
                    })
            
            # Sort by potential savings
            recommendations.sort(key=lambda x: x['potential_savings'], reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting consolidated recommendations: {e}")
            return []
    
    def create_multi_account_dashboard(self):
        """Create Streamlit dashboard for multi-account management"""
        st.set_page_config(
            page_title="Multi-Account Management",
            page_icon="🏢",
            layout="wide"
        )
        
        st.title("🏢 Multi-Account Cost Management")
        st.markdown("---")
        
        # Initialize multi-account manager
        manager = MultiAccountManager()
        
        # Sidebar controls
        st.sidebar.header("🏢 Account Controls")
        
        if st.sidebar.button("📊 Refresh Account Data"):
            with st.spinner("Refreshing account data..."):
                summary = manager.get_account_summary()
                st.session_state.account_summary = summary
        
        if st.sidebar.button("🔗 Setup Cross-Account Access"):
            with st.spinner("Setting up cross-account access..."):
                # Simulate setup for all accounts
                for account_id in manager.accounts.keys():
                    manager.create_cross_account_role(account_id)
                st.success("Cross-account access setup completed!")
        
        if st.sidebar.button("💡 Generate Consolidated Recommendations"):
            with st.spinner("Generating consolidated recommendations..."):
                recommendations = manager.get_consolidated_recommendations()
                st.session_state.consolidated_recommendations = recommendations
        
        # Display account summary
        if 'account_summary' in st.session_state:
            summary = st.session_state.account_summary
            
            st.header("📊 Account Summary")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Accounts",
                    summary['total_accounts'],
                    delta="managed accounts"
                )
            
            with col2:
                st.metric(
                    "Total Monthly Spend",
                    f"${summary['total_monthly_spend']:,.2f}",
                    delta="across all accounts"
                )
            
            with col3:
                st.metric(
                    "Optimization Potential",
                    f"${summary['total_optimization_potential']:,.2f}",
                    delta="potential savings"
                )
            
            with col4:
                savings_percentage = (summary['total_optimization_potential'] / summary['total_monthly_spend']) * 100
                st.metric(
                    "Savings Percentage",
                    f"{savings_percentage:.1f}%",
                    delta="of total spend"
                )
            
            # Account distribution charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Account Types")
                account_types_df = pd.DataFrame(
                    list(summary['account_types'].items()),
                    columns=['Type', 'Count']
                )
                fig_types = px.pie(account_types_df, values='Count', names='Type')
                st.plotly_chart(fig_types, use_container_width=True)
            
            with col2:
                st.subheader("Cost Centers")
                cost_centers_data = []
                for center, data in summary['cost_centers'].items():
                    cost_centers_data.append({
                        'Cost Center': center,
                        'Spend': data['spend'],
                        'Accounts': data['accounts']
                    })
                
                cost_centers_df = pd.DataFrame(cost_centers_data)
                fig_centers = px.bar(cost_centers_df, x='Cost Center', y='Spend', title='Spend by Cost Center')
                st.plotly_chart(fig_centers, use_container_width=True)
            
            # Top spending accounts
            st.subheader("Top Spending Accounts")
            top_accounts_df = pd.DataFrame(summary['top_accounts'])
            
            fig_top = px.bar(
                top_accounts_df,
                x='account_name',
                y='monthly_spend',
                title='Top Spending Accounts',
                labels={'monthly_spend': 'Monthly Spend ($)', 'account_name': 'Account Name'}
            )
            st.plotly_chart(fig_top, use_container_width=True)
        
        # Consolidated recommendations
        if 'consolidated_recommendations' in st.session_state:
            st.header("💡 Consolidated Optimization Recommendations")
            
            recommendations = st.session_state.consolidated_recommendations
            
            # Group by priority
            priority_groups = {}
            for rec in recommendations:
                priority = rec['priority']
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append(rec)
            
            for priority, recs in priority_groups.items():
                with st.expander(f"🎯 {priority.upper()} Priority Recommendations ({len(recs)} items)"):
                    for rec in recs:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**{rec['title']}**")
                            st.write(f"Account: {rec['account_name']} ({rec['account_id']})")
                            st.write(f"Cost Center: {rec['cost_center']}")
                            st.write(f"Description: {rec['description']}")
                        
                        with col2:
                            st.metric(
                                "Potential Savings",
                                f"${rec['potential_savings']:,.2f}",
                                delta="monthly"
                            )
                        
                        with col3:
                            st.write(f"**Effort**: {rec['effort'].title()}")
                            st.write(f"**Type**: {rec['type'].title()}")
        
        # Account details
        st.header("🏢 Account Details")
        
        accounts = manager.get_all_accounts()
        
        for account in accounts:
            with st.expander(f"📋 {account.account_name} ({account.account_id})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Account Type**: {account.account_type.value.title()}")
                    st.write(f"**Status**: {account.status.value.title()}")
                    st.write(f"**Region**: {account.region}")
                    st.write(f"**Cost Center**: {account.cost_center}")
                    st.write(f"**Owner**: {account.owner}")
                
                with col2:
                    st.metric("Monthly Spend", f"${account.monthly_spend:,.2f}")
                    st.metric("Optimization Potential", f"${account.optimization_potential:,.2f}")
                    
                    # Tags
                    st.write("**Tags**:")
                    for key, value in account.tags.items():
                        st.write(f"  • {key}: {value}")
        
        # Footer
        st.markdown("---")
        st.markdown("**Multi-Account Management System** - Cross-Account Cost Optimization")
        st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function to run multi-account management"""
    manager = MultiAccountManager()
    
    # Test multi-account system
    print("🏢 Testing Multi-Account Management System...")
    
    # Test account loading
    print("Testing account configurations...")
    accounts = manager.get_all_accounts()
    print(f"✅ Loaded {len(accounts)} accounts")
    
    # Test account summary
    print("Testing account summary...")
    summary = manager.get_account_summary()
    print(f"✅ Account summary - {summary['total_accounts']} accounts, ${summary['total_monthly_spend']:,.2f} total spend")
    
    # Test cross-account costs
    print("Testing cross-account cost data...")
    for account_id in list(manager.accounts.keys())[:2]:  # Test first 2 accounts
        cost_data = manager.get_cross_account_costs(account_id)
        print(f"✅ Cost data for {account_id}: ${cost_data['monthly_spend']:,.2f}")
    
    # Test consolidated recommendations
    print("Testing consolidated recommendations...")
    recommendations = manager.get_consolidated_recommendations()
    print(f"✅ Generated {len(recommendations)} consolidated recommendations")
    
    print("🎉 Multi-Account Management System is ready!")

if __name__ == "__main__":
    main()
