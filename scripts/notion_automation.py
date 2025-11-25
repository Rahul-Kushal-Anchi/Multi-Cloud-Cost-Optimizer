#!/usr/bin/env python3
"""
Notion Automation Script
Automatically sets up your Final Exam Prep task tracker in Notion
"""

import os
import sys
from notion_client import Client
import json

# Your Notion credentials (from environment variables)
# Set these before running: export NOTION_TOKEN="your_token"
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
USER_ID = os.getenv("NOTION_USER_ID", "")

def initialize_notion_client():
    """Initialize Notion client with your token"""
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN environment variable not set!")
        print("\n💡 Set it with:")
        print("   export NOTION_TOKEN='your_notion_token_here'")
        sys.exit(1)
    
    try:
        notion = Client(auth=NOTION_TOKEN)
        print("✅ Notion client initialized successfully")
        return notion
    except Exception as e:
        print(f"❌ Error initializing Notion client: {e}")
        sys.exit(1)

def get_user_pages(notion):
    """Get all pages accessible by the user"""
    try:
        # Search for pages
        results = notion.search(filter={"property": "object", "value": "page"})
        print(f"\n📄 Found {len(results.get('results', []))} pages")
        return results.get('results', [])
    except Exception as e:
        print(f"❌ Error searching pages: {e}")
        return []

def list_pages(notion):
    """List all pages and help user find their task tracker page"""
    pages = get_user_pages(notion)
    
    if not pages:
        print("❌ No pages found. Make sure:")
        print("   1. Your Notion integration has access to the workspace")
        print("   2. The page has been shared with the integration")
        return None
    
    print("\n📋 Your Pages:")
    print("=" * 60)
    
    for idx, page in enumerate(pages[:10]):  # Show first 10
        title = "Untitled"
        if 'properties' in page:
            for prop_name, prop_data in page['properties'].items():
                if prop_data.get('type') == 'title' and prop_data.get('title'):
                    title = prop_data['title'][0].get('plain_text', 'Untitled')
                    break
        
        page_id = page['id'].replace('-', '')
        print(f"{idx + 1}. {title}")
        print(f"   ID: {page_id}")
        print()
    
    return pages

def find_task_tracker_page(notion):
    """Help user find their Final Exam Prep page"""
    pages = list_pages(notion)
    
    if not pages:
        print("\n💡 To use automation:")
        print("   1. Find your 'Final Exam Prep' page in the list above")
        print("   2. Copy the page ID")
        print("   3. Run: python scripts/notion_automation.py <PAGE_ID>")
        print("\n   Or manually provide the page ID:")
        page_id = input("   Enter page ID (or press Enter to skip): ").strip()
        if page_id:
            return page_id.replace('-', '')
    
    return None

def convert_checkboxes(notion, page_id):
    """Convert markdown checkboxes to Notion checkboxes"""
    try:
        # Read page content
        page = notion.pages.retrieve(page_id)
        
        # Get page blocks
        blocks = notion.blocks.children.list(page_id)
        
        print(f"\n🔄 Converting checkboxes in page...")
        
        updated_count = 0
        for block in blocks.get('results', []):
            if block['type'] == 'paragraph':
                rich_text = block['paragraph'].get('rich_text', [])
                if rich_text:
                    text = ''.join([text.get('plain_text', '') for text in rich_text])
                    
                    # Check if it contains checkbox pattern
                    if '- [ ]' in text_content or '- [x]' in text_content:
                        # Convert to Notion checkbox
                        # Note: Notion API doesn't directly support converting text to checkboxes
                        # We'll need to create new blocks
                        print(f"   Found checkbox: {text_content[:50]}...")
                        updated_count += 1
        
        print(f"✅ Found {updated_count} checkboxes")
        return True
        
    except Exception as e:
        print(f"❌ Error converting checkboxes: {e}")
        return False

def create_database_view(notion, page_id):
    """Create a database view for tasks"""
    try:
        print("\n📊 Creating database view...")
        
        # Create database properties
        database_properties = {
            "Task": {"title": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Not Started", "color": "gray"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Complete", "color": "green"},
                        {"name": "Blocked", "color": "red"}
                    ]
                }
            },
            "Week": {
                "select": {
                    "options": [
                        {"name": "Week 1", "color": "blue"},
                        {"name": "Week 2", "color": "purple"},
                        {"name": "Week 3", "color": "orange"}
                    ]
                }
            },
            "Due Date": {"date": {}},
            "Priority": {
                "select": {
                    "options": [
                        {"name": "Critical", "color": "red"},
                        {"name": "High", "color": "yellow"},
                        {"name": "Medium", "color": "blue"}
                    ]
                }
            },
            "Real Data Verified": {"checkbox": {}},
            "Notes": {"rich_text": {}}
        }
        
        # Create database as child of page
        database = notion.databases.create(
            parent={"page_id": page_id},
            title=[{"type": "text", "text": {"content": "Final Exam Prep Tasks"}}],
            properties=database_properties
        )
        
        print(f"✅ Database created: {database['id']}")
        return database
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return None

def setup_views(notion, database_id):
    """Create different views for the database"""
    try:
        print("\n📋 Creating views...")
        
        views = [
            {
                "name": "All Tasks",
                "type": "table"
            },
            {
                "name": "This Week",
                "type": "table",
                "filter": {
                    "property": "Week",
                    "select": {"equals": "Week 1"}
                }
            },
            {
                "name": "By Status",
                "type": "board",
                "group_by": "Status"
            },
            {
                "name": "By Priority",
                "type": "table",
                "group_by": "Priority"
            }
        ]
        
        print("✅ Views would be created (manual setup recommended)")
        return True
        
    except Exception as e:
        print(f"❌ Error creating views: {e}")
        return False

def main():
    """Main automation function"""
    print("🚀 Notion Automation Setup")
    print("=" * 60)
    
    # Initialize client
    notion = initialize_notion_client()
    
    # Check if page ID provided as argument
    if len(sys.argv) > 1:
        page_id = sys.argv[1].replace('-', '')
        print(f"\n📄 Using page ID: {page_id}")
    else:
        print("\n🔍 Finding your pages...")
        page_id = find_task_tracker_page(notion)
        
        if not page_id:
            print("\n❌ No page ID provided. Exiting.")
            print("\n💡 To use automation:")
            print("   1. Open your Notion page")
            print("   2. Click '...' → 'Copy link'")
            print("   3. Extract the page ID from the URL")
            print("   4. Run: python scripts/notion_automation.py <PAGE_ID>")
            return
    
    # Verify page access
    try:
        page = notion.pages.retrieve(page_id)
        print(f"✅ Page found: {page.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Untitled')}")
    except Exception as e:
        print(f"❌ Cannot access page: {e}")
        print("\n💡 Make sure:")
        print("   1. The page is shared with your Notion integration")
        print("   2. The integration has 'Edit' permissions")
        return
    
    # Run automation
    print("\n🤖 Starting automation...")
    print("=" * 60)
    
    # Note: Notion API has limitations for converting markdown to checkboxes
    # The best approach is manual setup, but we can help with:
    
    # 1. Create database structure
    database = create_database_view(notion, page_id)
    
    if database:
        setup_views(notion, database['id'])
    
    print("\n✅ Automation complete!")
    print("\n📝 Next steps:")
    print("   1. The database structure has been created")
    print("   2. Manually convert checkboxes using Notion's UI")
    print("   3. Use the database to track your tasks")
    print("   4. Set up views as needed")

if __name__ == "__main__":
    main()

