#!/usr/bin/env python3
"""
Test script to check if we can access the Notion page
"""

import os
import sys
from notion_client import Client

# Load environment variables
def load_env():
    """Load .env file if it exists"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

load_env()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
PAGE_ID = "2898d3b7800c805f865bf5d8d26c9d0a"

if not NOTION_TOKEN:
    print("❌ NOTION_TOKEN not found!")
    print("💡 Make sure scripts/.env exists with NOTION_TOKEN")
    sys.exit(1)

print("🔍 Testing Notion Page Access")
print("=" * 60)
print(f"📄 Page ID: {PAGE_ID}")
print(f"🔑 Token: {NOTION_TOKEN[:20]}...")
print()

try:
    # Initialize client
    notion = Client(auth=NOTION_TOKEN)
    print("✅ Notion client initialized")
    
    # Try to access the page
    print(f"\n🔍 Attempting to access page...")
    page = notion.pages.retrieve(PAGE_ID)
    
    print("✅ SUCCESS! Page is accessible!")
    print()
    
    # Get page title
    title = "Untitled"
    if 'properties' in page:
        title_prop = page.get('properties', {}).get('title', {})
        if title_prop.get('title'):
            title = title_prop['title'][0].get('plain_text', 'Untitled')
    
    print(f"📄 Page Title: {title}")
    print(f"🆔 Page ID: {page['id']}")
    print()
    print("🎉 Your integration can access this page!")
    print("✅ You can now run the automation script!")
    
except Exception as e:
    print(f"❌ ERROR: Cannot access page")
    print(f"   Error: {e}")
    print()
    print("💡 This means:")
    print("   1. The page is NOT shared with the integration, OR")
    print("   2. The page ID is incorrect, OR")
    print("   3. The integration doesn't have access")
    print()
    print("🔧 To fix:")
    print("   1. Open: https://www.notion.so/2898d3b7800c805f865bf5d8d26c9d0a")
    print("   2. Click 'Share' → 'Add people, emails, groups, or integrations'")
    print("   3. Search for 'Cost Optimizer Tracker'")
    print("   4. Add it with 'Edit' permissions")
    print()
    print("💡 If the integration doesn't appear in search:")
    print("   - Make sure you're in the same workspace")
    print("   - Try refreshing the page")
    print("   - The script might still work - try running it anyway!")


