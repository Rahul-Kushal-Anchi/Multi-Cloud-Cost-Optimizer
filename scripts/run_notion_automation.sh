#!/bin/bash
# Quick script to run Notion automation
# 
# First, set your credentials:
# export NOTION_TOKEN="your_token_here"
# export NOTION_USER_ID="your_user_id_here"
#
# Or create a .env file in scripts/ directory

# Load from .env if it exists
if [ -f "$(dirname "$0")/.env" ]; then
    source "$(dirname "$0")/.env"
fi

# Check if token is set
if [ -z "$NOTION_TOKEN" ]; then
    echo "❌ NOTION_TOKEN not set!"
    echo ""
    echo "Set it with:"
    echo "  export NOTION_TOKEN='your_token'"
    echo ""
    echo "Or create scripts/.env file with:"
    echo "  NOTION_TOKEN=your_token"
    echo "  NOTION_USER_ID=your_user_id"
    exit 1
fi

cd "$(dirname "$0")/.."
python3 scripts/notion_automation.py "$@"

