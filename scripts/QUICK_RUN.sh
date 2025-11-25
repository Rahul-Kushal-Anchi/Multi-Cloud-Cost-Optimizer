#!/bin/bash
# Quick Run Script - Notion Automation
# This script does everything automatically!

echo "🚀 Notion Automation - Quick Setup"
echo "=================================="
echo ""

# Step 1: Check Python
echo "📦 Step 1: Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"
echo ""

# Step 2: Check/Install Notion client
echo "📦 Step 2: Checking Notion client..."
if ! python3 -c "import notion_client" 2>/dev/null; then
    echo "   Installing notion-client..."
    pip3 install --user notion-client > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Notion client installed"
    else
        echo "❌ Failed to install. Try: pip3 install notion-client"
        exit 1
    fi
else
    echo "✅ Notion client already installed"
fi
echo ""

# Step 3: Check .env file
echo "📋 Step 3: Checking credentials..."
if [ -f "scripts/.env" ]; then
    echo "✅ Credentials file found"
    source scripts/.env
else
    echo "❌ scripts/.env not found"
    echo "   Creating it now..."
    cat > scripts/.env << 'ENVEOF'
NOTION_TOKEN=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
NOTION_USER_ID=22dd872b-594c-814c-84b8-0002da5d3d3f
ENVEOF
    echo "✅ Created scripts/.env"
    source scripts/.env
fi
echo ""

# Step 4: Run automation
echo "🤖 Step 4: Running automation..."
echo "   (This will connect to your Notion account)"
echo ""

cd "$(dirname "$0")/.."
python3 scripts/notion_automation.py "$@"

echo ""
echo "✅ Done!"
