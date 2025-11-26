#!/bin/bash
# Quick script to format Notion page beautifully

if [ -z "$1" ]; then
    echo "❌ Page ID required!"
    echo "Usage: ./scripts/format_notion_page.sh <PAGE_ID>"
    exit 1
fi

PAGE_ID=$1

echo "🎨 Formatting Notion page..."
echo ""

# Load environment variables
set -a
source scripts/.env 2>/dev/null
set +a

# Run the formatting script
python3 scripts/notion_beautiful_formatting.py "$PAGE_ID"

