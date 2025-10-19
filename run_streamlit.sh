#!/bin/bash

# AWS Cost Optimizer - Streamlit Dashboard Launcher
echo "🚀 Starting AWS Cost Optimizer Dashboard..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r streamlit_requirements.txt

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable not set"
    echo "   The AI assistant will show placeholder messages"
    echo "   To enable AI features, set your OpenAI API key:"
    echo "   export OPENAI_API_KEY='your-api-key-here'"
    echo ""
fi

# Launch Streamlit
echo "🌟 Launching AWS Cost Optimizer Dashboard..."
echo "   Opening browser at: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

streamlit run streamlit_app.py
