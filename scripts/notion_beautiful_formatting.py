#!/usr/bin/env python3
"""
Beautiful Notion Page Formatter
Creates a beautifully formatted task tracker with headers, styles, callouts, and more
"""

import os
import sys
from notion_client import Client
from datetime import datetime, timedelta

# Load environment variables
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

load_env()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
PAGE_ID = sys.argv[1] if len(sys.argv) > 1 else None

if not NOTION_TOKEN:
    print("❌ NOTION_TOKEN not found!")
    sys.exit(1)

if not PAGE_ID:
    print("❌ Page ID required!")
    print("Usage: python3 notion_beautiful_formatting.py <PAGE_ID>")
    sys.exit(1)

notion = Client(auth=NOTION_TOKEN)

def create_heading_block(text, level=1):
    """Create a heading block"""
    return {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def create_callout_block(text, icon="💡", color="blue"):
    """Create a callout block"""
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"emoji": icon},
            "color": color
        }
    }

def create_divider():
    """Create a divider"""
    return {
        "object": "block",
        "type": "divider",
        "divider": {}
    }

def create_toggle_block(title, children=None):
    """Create a toggle/collapsible block"""
    block = {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": title}}]
        }
    }
    if children:
        block["has_children"] = True
    return block

def create_paragraph(text):
    """Create a paragraph block"""
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def create_bulleted_list_item(text):
    """Create a bulleted list item"""
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def create_numbered_list_item(text):
    """Create a numbered list item"""
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def create_quote(text):
    """Create a quote block"""
    return {
        "object": "block",
        "type": "quote",
        "quote": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def create_code_block(code, language="plain text"):
    """Create a code block"""
    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": code}}],
            "language": language
        }
    }

def format_page_beautifully(page_id):
    """Format the Notion page with beautiful styling"""
    print("🎨 Formatting Notion page with beautiful styles...")
    print("=" * 60)
    
    # Clear existing content (optional - comment out if you want to keep existing)
    # For now, we'll append to the page
    
    blocks = []
    
    # 1. Hero Section with Title
    blocks.append(create_heading_block("🚀 Final Exam Preparation - ML Cost Optimizer", 1))
    blocks.append(create_callout_block(
        "Complete your ML-powered cost optimization platform by December 13, 2025. Track your progress daily and ensure all features use REAL data only.",
        icon="🎯",
        color="blue"
    ))
    blocks.append(create_divider())
    
    # 2. Quick Stats Section
    blocks.append(create_heading_block("📊 Quick Stats", 2))
    blocks.append(create_callout_block(
        "Track your progress: Tasks completed, ML models deployed, Real data verified",
        icon="📈",
        color="green"
    ))
    blocks.append(create_divider())
    
    # 3. Week 1 Section
    blocks.append(create_heading_block("📅 Week 1: ML Foundation & Anomaly Detection", 2))
    blocks.append(create_callout_block(
        "Goal: Deploy ML-powered anomaly detection using REAL AWS CUR data",
        icon="🔍",
        color="purple"
    ))
    
    # Week 1 Tasks
    week1_tasks = [
        "Set up ML training environment (scikit-learn, pandas, numpy)",
        "Create api/ml/ directory structure",
        "Set up CloudWatch metrics collection (REAL data only)",
        "Train Isolation Forest model on REAL AWS CUR data (90 days)",
        "Implement anomaly detection API endpoint",
        "Build anomaly detection UI dashboard",
        "Test with REAL anomalies from your AWS account"
    ]
    
    blocks.append(create_toggle_block("Days 1-2: Infrastructure Setup"))
    for task in week1_tasks[:3]:
        blocks.append(create_bulleted_list_item(f"☐ {task}"))
    
    blocks.append(create_toggle_block("Days 3-4: Anomaly Detection Model"))
    for task in week1_tasks[3:5]:
        blocks.append(create_bulleted_list_item(f"☐ {task}"))
    
    blocks.append(create_toggle_block("Days 5-7: Anomaly Detection UI"))
    for task in week1_tasks[5:]:
        blocks.append(create_bulleted_list_item(f"☐ {task}"))
    
    blocks.append(create_divider())
    
    # 4. Week 2 Section
    blocks.append(create_heading_block("📅 Week 2: Right-Sizing & CloudWatch Integration", 2))
    blocks.append(create_callout_block(
        "Goal: Deploy intelligent right-sizing recommendations with specific savings ($X/month)",
        icon="💰",
        color="orange"
    ))
    
    week2_tasks = [
        "Collect REAL EC2 CloudWatch metrics (CPU, memory, network)",
        "Store metrics in database",
        "Train K-means clustering model",
        "Implement right-sizing recommendation engine",
        "Calculate specific savings (e.g., 'Save $73/month')",
        "Build right-sizing recommendation UI",
        "Show 'Apply Recommendation' flow"
    ]
    
    blocks.append(create_toggle_block("Days 1-2: CloudWatch Metrics Collection"))
    for task in week2_tasks[:2]:
        blocks.append(create_bulleted_list_item(f"☐ {task}"))
    
    blocks.append(create_toggle_block("Days 3-4: Right-Sizing Model"))
    for task in week2_tasks[2:5]:
        blocks.append(create_bulleted_list_item(f"☐ {task}"))
    
    blocks.append(create_toggle_block("Days 5-7: Right-Sizing UI"))
    for task in week2_tasks[5:]:
        blocks.append(create_bulleted_list_item(f"☐ {task}"))
    
    blocks.append(create_divider())
    
    # 5. Week 3 Section
    blocks.append(create_heading_block("📅 Week 3: Forecasting & Polish", 2))
    blocks.append(create_callout_block(
        "Goal: Complete ML features and polish for presentation",
        icon="✨",
        color="pink"
    ))
    
    week3_tasks = [
        "Train Prophet/LSTM forecasting model",
        "Implement forecasting API endpoint",
        "Build forecasting dashboard with confidence intervals",
        "Improve all ML visualizations",
        "Add loading states and error handling",
        "Mobile responsiveness",
        "Presentation preparation"
    ]
    
    blocks.append(create_toggle_block("Days 1-2: Cost Forecasting"))
    for task in week3_tasks[:3]:
        blocks.append(create_bulleted_list_item(f"☐ {task}"))
    
    blocks.append(create_toggle_block("Days 3-4: UI/UX Polish"))
    for task in week3_tasks[3:6]:
        blocks.append(create_bulleted_list_item(f"☐ {task}"))
    
    blocks.append(create_toggle_block("Days 5-7: Presentation Prep"))
    blocks.append(create_bulleted_list_item(f"☐ {week3_tasks[6]}"))
    
    blocks.append(create_divider())
    
    # 6. Critical Requirements
    blocks.append(create_heading_block("⚠️ Critical Requirements", 2))
    blocks.append(create_callout_block(
        "ALL implementations must use REAL data only. NO mock or demo data allowed!",
        icon="🚨",
        color="red"
    ))
    
    requirements = [
        "Use REAL AWS CUR data for training (minimum 90 days)",
        "Collect REAL CloudWatch metrics (CPU, memory, network)",
        "Train models on REAL historical patterns",
        "Test with REAL anomalies from your AWS account",
        "Show REAL right-sizing recommendations with actual savings",
        "Forecast using REAL cost trends"
    ]
    
    for req in requirements:
        blocks.append(create_bulleted_list_item(f"✅ {req}"))
    
    blocks.append(create_divider())
    
    # 7. Success Metrics
    blocks.append(create_heading_block("🎯 Success Metrics", 2))
    blocks.append(create_quote("Demonstrate these in your presentation:"))
    
    metrics = [
        "Find at least 1 REAL anomaly in your AWS account",
        "Show 1 right-sizing recommendation with specific savings ($X/month)",
        "Display 30-day cost forecast with confidence intervals",
        "All models trained on REAL AWS data (not mock)"
    ]
    
    for metric in metrics:
        blocks.append(create_numbered_list_item(metric))
    
    blocks.append(create_divider())
    
    # 8. Daily Progress Tracker
    blocks.append(create_heading_block("📝 Daily Progress Tracker", 2))
    blocks.append(create_callout_block(
        "Update this section daily with what you completed",
        icon="📅",
        color="yellow"
    ))
    
    today = datetime.now().strftime("%B %d, %Y")
    blocks.append(create_heading_block(f"Today: {today}", 3))
    blocks.append(create_paragraph("What I completed today:"))
    blocks.append(create_bulleted_list_item("• "))
    blocks.append(create_paragraph("What I'm working on tomorrow:"))
    blocks.append(create_bulleted_list_item("• "))
    blocks.append(create_paragraph("Blockers/Issues:"))
    blocks.append(create_bulleted_list_item("• None"))
    
    blocks.append(create_divider())
    
    # 9. Resources & Links
    blocks.append(create_heading_block("🔗 Resources & Links", 2))
    blocks.append(create_paragraph("Important documentation:"))
    blocks.append(create_bulleted_list_item("ML Cost Optimization Roadmap"))
    blocks.append(create_bulleted_list_item("ML Models Implementation Plan"))
    blocks.append(create_bulleted_list_item("Production Requirements (REAL DATA ONLY)"))
    blocks.append(create_bulleted_list_item("World-Class Engineer Recommendations"))
    
    blocks.append(create_divider())
    
    # 10. Final Notes
    blocks.append(create_heading_block("💡 Notes", 2))
    blocks.append(create_callout_block(
        "Remember: ML features differentiate you from competitors. Focus on Anomaly Detection first, then Right-Sizing, then Forecasting.",
        icon="💭",
        color="gray"
    ))
    
    # Append all blocks to the page
    print(f"\n📝 Adding {len(blocks)} formatted blocks to page...")
    
    try:
        # Append blocks in batches (Notion API limit is 100 blocks per request)
        batch_size = 100
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            notion.blocks.children.append(
                block_id=page_id,
                children=batch
            )
            print(f"✅ Added blocks {i+1}-{min(i+batch_size, len(blocks))}")
        
        print("\n✅ Beautiful formatting complete!")
        print("\n🎨 Your Notion page now has:")
        print("   ✅ Headers and sections")
        print("   ✅ Callout boxes with colors")
        print("   ✅ Toggle lists (collapsible sections)")
        print("   ✅ Bulleted and numbered lists")
        print("   ✅ Dividers and quotes")
        print("   ✅ Emojis and icons")
        print("   ✅ Organized structure")
        
    except Exception as e:
        print(f"❌ Error formatting page: {e}")
        print("\n💡 Make sure:")
        print("   1. The page is shared with your integration")
        print("   2. The integration has 'Edit' permissions")
        return False
    
    return True

if __name__ == "__main__":
    if not PAGE_ID:
        print("❌ Page ID required!")
        print("Usage: python3 notion_beautiful_formatting.py <PAGE_ID>")
        sys.exit(1)
    
    print("🎨 Beautiful Notion Page Formatter")
    print("=" * 60)
    print(f"📄 Page ID: {PAGE_ID}")
    print()
    
    # Verify page access
    try:
        page = notion.pages.retrieve(PAGE_ID)
        title = "Untitled"
        if 'properties' in page:
            title_prop = page.get('properties', {}).get('title', {})
            if title_prop.get('title'):
                title = title_prop['title'][0].get('plain_text', 'Untitled')
        print(f"✅ Page found: {title}")
    except Exception as e:
        print(f"❌ Cannot access page: {e}")
        print("\n💡 Make sure:")
        print("   1. The page is shared with your integration")
        print("   2. The integration has 'Edit' permissions")
        sys.exit(1)
    
    # Format the page
    success = format_page_beautifully(PAGE_ID)
    
    if success:
        print("\n🎉 Done! Check your Notion page - it should be beautifully formatted now!")
    else:
        print("\n❌ Failed to format page. Check the error above.")


