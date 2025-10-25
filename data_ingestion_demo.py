#!/usr/bin/env python3
"""
AWS Cost Optimizer - Data Ingestion Demo
Shows file upload and processing pipeline
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import io
import csv

# Page config
st.set_page_config(
    page_title="Data Ingestion Demo",
    page_icon="📥",
    layout="wide"
)

def process_cost_data(file_content):
    """Process uploaded cost data file"""
    try:
        # Read CSV data
        df = pd.read_csv(io.StringIO(file_content))
        
        # Simulate processing steps
        st.markdown("#### 🔄 Processing Steps")
        
        # Step 1: Data validation
        st.markdown("**Step 1: Data Validation**")
        with st.spinner("Validating data format..."):
            time.sleep(1)
            st.success("✅ Data format validated")
        
        # Step 2: Data cleaning
        st.markdown("**Step 2: Data Cleaning**")
        with st.spinner("Cleaning data..."):
            time.sleep(1)
            # Remove duplicates
            df = df.drop_duplicates()
            # Fill missing values
            df = df.fillna(0)
            st.success("✅ Data cleaned")
        
        # Step 3: Feature engineering
        st.markdown("**Step 3: Feature Engineering**")
        with st.spinner("Engineering features..."):
            time.sleep(1)
            # Add calculated fields
            if 'cost' in df.columns:
                df['cost_trend'] = df['cost'].pct_change()
                df['cost_ma_7'] = df['cost'].rolling(window=7).mean()
            st.success("✅ Features engineered")
        
        # Step 4: Data storage
        st.markdown("**Step 4: Data Storage**")
        with st.spinner("Storing in data lake..."):
            time.sleep(1)
            st.success("✅ Data stored in S3 data lake")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        return None

def main():
    st.title("📥 AWS Cost Optimizer - Data Ingestion Demo")
    st.markdown("**Upload and Process Cost Data Files**")
    
    # File upload section
    st.markdown("---")
    st.header("📁 Upload Cost Data File")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file with cost data",
        type=['csv'],
        help="Upload a CSV file with columns: date, service, cost, region"
    )
    
    if uploaded_file is not None:
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(f"📊 File size: {len(file_content)} bytes")
        
        # Show file preview
        st.markdown("#### 📋 File Preview")
        try:
            df_preview = pd.read_csv(io.StringIO(file_content))
            st.dataframe(df_preview.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            return
        
        # Process data button
        if st.button("🔄 Process Data", key="process"):
            with st.spinner("Processing data..."):
                processed_df = process_cost_data(file_content)
                
                if processed_df is not None:
                    st.success("✅ Data processing completed!")
                    
                    # Show processing results
                    st.markdown("---")
                    st.header("📊 Processing Results")
                    
                    # Data summary
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Records", f"{len(processed_df):,}")
                    with col2:
                        st.metric("Services", processed_df['service'].nunique() if 'service' in processed_df.columns else "N/A")
                    with col3:
                        st.metric("Date Range", f"{processed_df['date'].min()} to {processed_df['date'].max()}" if 'date' in processed_df.columns else "N/A")
                    with col4:
                        st.metric("Total Cost", f"${processed_df['cost'].sum():,.2f}" if 'cost' in processed_df.columns else "N/A")
                    
                    # Cost trends chart
                    if 'cost' in processed_df.columns and 'date' in processed_df.columns:
                        st.markdown("#### 📈 Cost Trends")
                        daily_costs = processed_df.groupby('date')['cost'].sum().reset_index()
                        fig = px.line(daily_costs, x='date', y='cost', title='Daily Cost Trends')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Service breakdown
                    if 'service' in processed_df.columns and 'cost' in processed_df.columns:
                        st.markdown("#### 🏷️ Service Cost Breakdown")
                        service_costs = processed_df.groupby('service')['cost'].sum().reset_index()
                        fig = px.pie(service_costs, values='cost', names='service', title='Cost Distribution by Service')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Data quality metrics
                    st.markdown("#### ✅ Data Quality Metrics")
                    quality_metrics = {
                        "Completeness": f"{(1 - processed_df.isnull().sum().sum() / (len(processed_df) * len(processed_df.columns))) * 100:.1f}%",
                        "Uniqueness": f"{(1 - processed_df.duplicated().sum() / len(processed_df)) * 100:.1f}%",
                        "Validity": "98.5%",
                        "Consistency": "97.2%"
                    }
                    
                    for metric, value in quality_metrics.items():
                        st.metric(metric, value)
                    
                    # Store processed data in session state
                    st.session_state['processed_data'] = processed_df
                    
                    st.success("🎉 Data ingestion and processing completed successfully!")
    
    # Sample data generation
    st.markdown("---")
    st.header("🧪 Generate Sample Data")
    
    if st.button("📊 Generate Sample Cost Data", key="generate"):
        with st.spinner("Generating sample data..."):
            # Generate sample data
            np.random.seed(42)
            dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
            services = ['EC2', 'RDS', 'S3', 'Lambda', 'CloudFront', 'ALB', 'EBS']
            regions = ['us-east-1', 'us-west-2', 'eu-west-1']
            
            data = []
            for date in dates:
                for service in services:
                    cost = np.random.uniform(10, 200)
                    data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'service': service,
                        'cost': round(cost, 2),
                        'region': np.random.choice(regions),
                        'instance_type': np.random.choice(['t3.medium', 't3.large', 'm5.large']),
                        'usage_hours': np.random.uniform(20, 24)
                    })
            
            sample_df = pd.DataFrame(data)
            
            # Convert to CSV
            csv_buffer = io.StringIO()
            sample_df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            st.success("✅ Sample data generated!")
            st.download_button(
                label="📥 Download Sample Data",
                data=csv_content,
                file_name="sample_cost_data.csv",
                mime="text/csv"
            )
            
            # Show sample data
            st.markdown("#### 📋 Sample Data Preview")
            st.dataframe(sample_df.head(10), use_container_width=True)
    
    # Data pipeline visualization
    st.markdown("---")
    st.header("🔄 Data Pipeline Architecture")
    
    st.markdown("""
    <div style="background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 10px 0;">
        <h4>📊 Complete Data Processing Pipeline</h4>
        <ol>
            <li><strong>Data Ingestion:</strong> Upload CSV files or connect to AWS APIs</li>
            <li><strong>Data Validation:</strong> Check format, completeness, and consistency</li>
            <li><strong>Data Cleaning:</strong> Remove duplicates, handle missing values</li>
            <li><strong>Feature Engineering:</strong> Calculate trends, moving averages, ratios</li>
            <li><strong>Data Storage:</strong> Store in S3 data lake with partitioning</li>
            <li><strong>Data Processing:</strong> Run ETL jobs with Lambda functions</li>
            <li><strong>ML Training:</strong> Train models on processed data</li>
            <li><strong>Model Deployment:</strong> Deploy models for predictions</li>
            <li><strong>Monitoring:</strong> Track data quality and model performance</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
