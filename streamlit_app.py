import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from openai import OpenAI
import os

# Page configuration
st.set_page_config(
    page_title="AWS Cost Optimizer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
client = OpenAI(api_key=OPENAI_API_KEY)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .cost-savings {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sample data for demonstration
@st.cache_data
def get_sample_cost_data():
    """Generate sample AWS cost data for demonstration"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    
    # Generate realistic cost data with some variability
    base_cost = 1500
    cost_data = []
    
    for i, date in enumerate(dates):
        # Add some realistic variation
        variation = (i % 7) * 50 + (i % 3) * 100  # Weekly and random patterns
        daily_cost = base_cost + variation + (i * 2)  # Slight upward trend
        
        cost_data.append({
            'date': date,
            'total_cost': daily_cost,
            'ec2_cost': daily_cost * 0.4,
            's3_cost': daily_cost * 0.15,
            'rds_cost': daily_cost * 0.25,
            'other_cost': daily_cost * 0.2
        })
    
    return pd.DataFrame(cost_data)

@st.cache_data
def get_recommendations():
    """Get cost optimization recommendations"""
    return [
        {
            'title': 'Rightsize EC2 Instances',
            'savings': 847,
            'effort': 'Medium',
            'impact': 'High',
            'description': 'Downsize over-provisioned EC2 instances based on CPU and memory utilization',
            'implementation': 'Use AWS Compute Optimizer and CloudWatch metrics'
        },
        {
            'title': 'Delete Unattached EBS Volumes',
            'savings': 312,
            'effort': 'Low',
            'impact': 'Medium',
            'description': 'Remove unused EBS volumes that are not attached to any instances',
            'implementation': 'Run AWS CLI script to identify and delete unattached volumes'
        },
        {
            'title': 'Schedule Non-Production Resources',
            'savings': 1245,
            'effort': 'Medium',
            'impact': 'High',
            'description': 'Stop non-production instances during nights and weekends',
            'implementation': 'Use AWS Instance Scheduler or Lambda functions'
        },
        {
            'title': 'Purchase Reserved Instances',
            'savings': 2100,
            'effort': 'High',
            'impact': 'High',
            'description': 'Commit to 1-3 year Reserved Instances for predictable workloads',
            'implementation': 'Analyze usage patterns and purchase RIs for stable workloads'
        },
        {
            'title': 'Clean Up Old Snapshots',
            'savings': 89,
            'effort': 'Low',
            'impact': 'Low',
            'description': 'Delete old EBS snapshots that are no longer needed',
            'implementation': 'Set up lifecycle policies for automatic cleanup'
        }
    ]

def get_ai_recommendation(user_query):
    """Get AI-powered recommendation using OpenAI"""
    try:
        if OPENAI_API_KEY == "your-openai-api-key-here":
            return "Please set your OpenAI API key in the environment variable OPENAI_API_KEY to use AI recommendations."
        
        # Create context-aware prompt
        prompt = f"""
        You are an AWS cost optimization expert. The user is asking: "{user_query}"
        
        Current AWS spending context:
        - Daily average: $1,500
        - Monthly total: ~$45,000
        - Top services: EC2 (40%), RDS (25%), S3 (15%), Other (20%)
        
        Provide actionable, specific recommendations for AWS cost optimization.
        Focus on:
        1. Immediate actions they can take
        2. Potential savings in dollars
        3. Implementation steps
        4. Best practices
        
        Keep response concise and practical.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting AI recommendation: {str(e)}"

# Main app
def main():
    st.title("💰 AWS Cost Optimizer")
    st.markdown("---")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigate",
        ["📊 Dashboard", "🤖 AI Assistant", "💡 Recommendations", "🔔 Alerts", "📈 Analytics"]
    )
    
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🤖 AI Assistant":
        show_ai_assistant()
    elif page == "💡 Recommendations":
        show_recommendations()
    elif page == "🔔 Alerts":
        show_alerts()
    elif page == "📈 Analytics":
        show_analytics()

def show_dashboard():
    st.header("📊 Cost Dashboard")
    
    # Get sample data
    cost_data = get_sample_cost_data()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_cost = cost_data['total_cost'].iloc[-1]
        st.metric(
            "Today's Cost",
            f"${current_cost:,.0f}",
            delta=f"${current_cost - cost_data['total_cost'].iloc[-2]:,.0f}"
        )
    
    with col2:
        avg_cost = cost_data['total_cost'].mean()
        st.metric(
            "30-Day Average",
            f"${avg_cost:,.0f}",
            delta=f"${avg_cost - cost_data['total_cost'].iloc[-8]:,.0f}"
        )
    
    with col3:
        monthly_projection = avg_cost * 30
        st.metric(
            "Monthly Projection",
            f"${monthly_projection:,.0f}",
            delta="5.2%"
        )
    
    with col4:
        total_savings = 4593  # Sum of all recommendations
        st.metric(
            "Potential Savings",
            f"${total_savings:,}/month",
            delta="23%"
        )
    
    st.markdown("---")
    
    # Cost trend chart
    st.subheader("📈 30-Day Cost Trend")
    fig = px.line(cost_data, x='date', y='total_cost', 
                  title="Daily AWS Costs", 
                  labels={'total_cost': 'Daily Cost ($)', 'date': 'Date'})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Service breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Service Breakdown")
        latest_costs = {
            'EC2': cost_data['ec2_cost'].iloc[-1],
            'RDS': cost_data['rds_cost'].iloc[-1],
            'S3': cost_data['s3_cost'].iloc[-1],
            'Other': cost_data['other_cost'].iloc[-1]
        }
        
        fig = px.pie(values=list(latest_costs.values()), 
                     names=list(latest_costs.keys()),
                     title="Today's Cost by Service")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📋 Cost Details")
        cost_df = pd.DataFrame([
            {"Service": "EC2", "Current": f"${latest_costs['EC2']:,.0f}", "30-Day Avg": f"${cost_data['ec2_cost'].mean():,.0f}", "Total": f"${cost_data['ec2_cost'].sum():,.0f}"},
            {"Service": "RDS", "Current": f"${latest_costs['RDS']:,.0f}", "30-Day Avg": f"${cost_data['rds_cost'].mean():,.0f}", "Total": f"${cost_data['rds_cost'].sum():,.0f}"},
            {"Service": "S3", "Current": f"${latest_costs['S3']:,.0f}", "30-Day Avg": f"${cost_data['s3_cost'].mean():,.0f}", "Total": f"${cost_data['s3_cost'].sum():,.0f}"},
            {"Service": "Other", "Current": f"${latest_costs['Other']:,.0f}", "30-Day Avg": f"${cost_data['other_cost'].mean():,.0f}", "Total": f"${cost_data['other_cost'].sum():,.0f}"}
        ])
        st.dataframe(cost_df, use_container_width=True)

def show_ai_assistant():
    st.header("🤖 AI Cost Optimization Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Quick question buttons
    st.subheader("💬 Quick Questions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💡 How can I reduce my EC2 costs?"):
            st.session_state.messages.append({"role": "user", "content": "How can I reduce my EC2 costs?"})
            response = get_ai_recommendation("How can I reduce my EC2 costs?")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("🔍 What are my top cost savings opportunities?"):
            st.session_state.messages.append({"role": "user", "content": "What are my top cost savings opportunities?"})
            response = get_ai_recommendation("What are my top cost savings opportunities?")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("⚠️ Are there any cost anomalies?"):
            st.session_state.messages.append({"role": "user", "content": "Are there any cost anomalies?"})
            response = get_ai_recommendation("Are there any cost anomalies?")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("📊 What's my cost optimization strategy?"):
            st.session_state.messages.append({"role": "user", "content": "What's my cost optimization strategy?"})
            response = get_ai_recommendation("What's my cost optimization strategy?")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about AWS cost optimization..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = get_ai_recommendation(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def show_recommendations():
    st.header("💡 Cost Optimization Recommendations")
    
    recommendations = get_recommendations()
    total_savings = sum(rec['savings'] for rec in recommendations)
    
    # Total savings banner
    st.markdown(f"""
    <div class="cost-savings">
        <h2>💰 Total Potential Monthly Savings: ${total_savings:,}</h2>
        <p>Average savings rate: 23% of current AWS spending</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recommendations grid
    for i, rec in enumerate(recommendations):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"{i+1}. {rec['title']}")
                st.write(f"**Description:** {rec['description']}")
                st.write(f"**Implementation:** {rec['implementation']}")
                
                # Effort and Impact indicators
                effort_colors = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}
                impact_colors = {'Low': '🔵', 'Medium': '🟠', 'High': '🔥'}
                
                st.write(f"**Effort:** {effort_colors[rec['effort']]} {rec['effort']} | **Impact:** {impact_colors[rec['impact']]} {rec['impact']}")
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #2e8b57;">${rec['savings']:,}</h3>
                    <p>Monthly Savings</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View Details", key=f"view_{i}"):
                    st.info(f"Detailed implementation guide for {rec['title']} would be shown here.")
            
            st.markdown("---")

def show_alerts():
    st.header("🔔 Cost Alerts & Anomalies")
    
    # Sample alerts
    alerts = [
        {
            'type': 'Critical',
            'title': 'Unusual EC2 Cost Spike',
            'description': 'EC2 costs increased by 45% compared to last week',
            'amount': '$2,340',
            'time': '2 hours ago',
            'status': 'Active'
        },
        {
            'type': 'Warning',
            'title': 'High S3 Storage Costs',
            'description': 'S3 costs 30% above average for the month',
            'amount': '$890',
            'time': '5 hours ago',
            'status': 'Active'
        },
        {
            'type': 'Info',
            'title': 'Reserved Instance Expiring',
            'description': '3 Reserved Instances expiring in 30 days',
            'amount': '$1,200',
            'time': '1 day ago',
            'status': 'Active'
        }
    ]
    
    # Alert metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Alerts", "3", delta="1")
    
    with col2:
        st.metric("Critical Issues", "1", delta="0")
    
    with col3:
        st.metric("Potential Impact", "$3,230", delta="+$1,100")
    
    st.markdown("---")
    
    # Alert list
    for alert in alerts:
        color_map = {'Critical': '🔴', 'Warning': '🟡', 'Info': '🔵'}
        
        with st.container():
            st.markdown(f"""
            <div style="border-left: 4px solid {'#ff4444' if alert['type'] == 'Critical' else '#ffaa00' if alert['type'] == 'Warning' else '#0088ff'}; padding: 15px; margin: 10px 0; background-color: #f8f9fa; border-radius: 5px;">
                <h4>{color_map[alert['type']]} {alert['title']}</h4>
                <p><strong>Impact:</strong> {alert['amount']} | <strong>Time:</strong> {alert['time']} | <strong>Status:</strong> {alert['status']}</p>
                <p>{alert['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("Investigate", key=f"investigate_{alert['title']}"):
                    st.info("Investigation details would be shown here.")
        with col2:
                if st.button("Dismiss", key=f"dismiss_{alert['title']}"):
                    st.success("Alert dismissed.")
            
            st.markdown("---")

def show_analytics():
    st.header("📈 Advanced Analytics")
    
    cost_data = get_sample_cost_data()
    
    # ML Forecast
    st.subheader("🔮 30-Day Cost Forecast")
    
    # Simple linear regression for demonstration
    import numpy as np
    from sklearn.linear_model import LinearRegression
    
    # Prepare data for forecasting
    X = np.array(range(len(cost_data))).reshape(-1, 1)
    y = cost_data['total_cost'].values
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate forecast
    future_days = 30
    future_X = np.array(range(len(cost_data), len(cost_data) + future_days)).reshape(-1, 1)
    forecast = model.predict(future_X)
    
    # Create forecast dates
    last_date = cost_data['date'].iloc[-1]
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=future_days, freq='D')
    
    # Plot actual vs forecast
    fig = go.Figure()
    
    # Actual data
    fig.add_trace(go.Scatter(
        x=cost_data['date'],
        y=cost_data['total_cost'],
        mode='lines',
        name='Actual Costs',
        line=dict(color='blue')
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=forecast,
        mode='lines',
        name='Forecast',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title="Cost Forecast (Next 30 Days)",
        xaxis_title="Date",
        yaxis_title="Daily Cost ($)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Service distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Service Cost Distribution")
        service_data = {
            'EC2': cost_data['ec2_cost'].sum(),
            'RDS': cost_data['rds_cost'].sum(),
            'S3': cost_data['s3_cost'].sum(),
            'Other': cost_data['other_cost'].sum()
        }
        
        fig = px.bar(x=list(service_data.keys()), y=list(service_data.values()),
                     title="Total Costs by Service (30 Days)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Multi-Service Trends")
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=cost_data['date'], y=cost_data['ec2_cost'], 
                                mode='lines', name='EC2', stackgroup='one'))
        fig.add_trace(go.Scatter(x=cost_data['date'], y=cost_data['rds_cost'], 
                                mode='lines', name='RDS', stackgroup='one'))
        fig.add_trace(go.Scatter(x=cost_data['date'], y=cost_data['s3_cost'], 
                                mode='lines', name='S3', stackgroup='one'))
        fig.add_trace(go.Scatter(x=cost_data['date'], y=cost_data['other_cost'], 
                                mode='lines', name='Other', stackgroup='one'))
        
        fig.update_layout(title="Service Cost Trends (Stacked)", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Analysis
    st.subheader("🤖 AI-Powered Analysis")
    
    if st.button("Get Deep Cost Analysis"):
        with st.spinner("Analyzing your cost patterns..."):
            analysis = get_ai_recommendation("Provide a comprehensive analysis of my AWS cost patterns and strategic recommendations for optimization")
            st.markdown(analysis)

if __name__ == "__main__":
    main()
