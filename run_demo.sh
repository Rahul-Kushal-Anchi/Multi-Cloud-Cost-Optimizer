#!/bin/bash

echo "🚀 AWS Cost Optimizer - Complete Working Demo"
echo "=============================================="
echo ""
echo "This demo shows the complete working pipeline:"
echo "✅ Data ingestion and processing"
echo "✅ ML model execution"
echo "✅ Dashboard visualization"
echo "✅ API response simulation"
echo ""
echo "Choose your demo:"
echo ""
echo "1. Complete Working Demo (Recommended)"
echo "2. Data Ingestion Demo"
echo "3. Working Pipeline Demo"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🚀 Starting Complete Working Demo..."
        streamlit run complete_working_demo.py --server.port 8501 --server.headless true
        ;;
    2)
        echo "📥 Starting Data Ingestion Demo..."
        streamlit run data_ingestion_demo.py --server.port 8502 --server.headless true
        ;;
    3)
        echo "⚙️ Starting Working Pipeline Demo..."
        streamlit run working_demo_pipeline.py --server.port 8503 --server.headless true
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
