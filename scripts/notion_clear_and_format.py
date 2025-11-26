#!/usr/bin/env python3
"""
Clear Notion page and add beautiful formatting
"""

import os
import sys
from notion_client import Client

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
    print("Usage: python3 notion_clear_and_format.py <PAGE_ID>")
    sys.exit(1)

notion = Client(auth=NOTION_TOKEN)

def clear_page_blocks(page_id):
    """Clear all blocks from the page"""
    print("🧹 Clearing existing page content...")
    
    try:
        # Get all blocks
        blocks_response = notion.blocks.children.list(block_id=page_id)
        blocks = blocks_response.get('results', [])
        
        if not blocks:
            print("✅ Page is already empty")
            return True
        
        print(f"📄 Found {len(blocks)} blocks to remove...")
        
        # Delete all blocks
        for i, block in enumerate(blocks, 1):
            try:
                notion.blocks.delete(block_id=block['id'])
                if i % 10 == 0:
                    print(f"   Removed {i}/{len(blocks)} blocks...")
            except Exception as e:
                print(f"   ⚠️  Could not remove block {i}: {e}")
        
        print(f"✅ Cleared {len(blocks)} blocks")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing page: {e}")
        return False

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

def create_toggle_block(title):
    """Create a toggle/collapsible block"""
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": title}}]
        }
    }

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

def format_page_beautifully(page_id):
    """Format the Notion page with beautiful styling"""
    print("\n🎨 Creating beautiful formatted content...")
    print("=" * 60)
    
    blocks = []
    
    # 1. Hero Section
    blocks.append(create_heading_block("🚀 Final Exam Preparation - ML Cost Optimizer", 1))
    blocks.append(create_callout_block(
        "Complete your ML-powered cost optimization platform by December 13, 2025. Track your progress daily and ensure all features use REAL data only.",
        icon="🎯",
        color="blue"
    ))
    blocks.append(create_divider())
    
    # 2. Quick Stats
    blocks.append(create_heading_block("📊 Quick Stats", 2))
    blocks.append(create_callout_block(
        "Track your progress: Tasks completed, ML models deployed, Real data verified",
        icon="📈",
        color="green"
    ))
    blocks.append(create_divider())
    
    # 3. Week 1
    blocks.append(create_heading_block("📅 Week 1: ML Foundation & Anomaly Detection", 2))
    blocks.append(create_callout_block(
        "Goal: Deploy ML-powered anomaly detection using REAL AWS CUR data",
        icon="🔍",
        color="purple"
    ))
    
    blocks.append(create_toggle_block("Days 1-2: Infrastructure Setup"))
    blocks.append(create_bulleted_list_item("☐ Set up ML training environment (scikit-learn, pandas, numpy)"))
    blocks.append(create_bulleted_list_item("☐ Create api/ml/ directory structure"))
    blocks.append(create_bulleted_list_item("☐ Set up CloudWatch metrics collection (REAL data only)"))
    
    blocks.append(create_toggle_block("Days 3-4: Anomaly Detection Model"))
    blocks.append(create_bulleted_list_item("☐ Train Isolation Forest model on REAL AWS CUR data (90 days)"))
    blocks.append(create_bulleted_list_item("☐ Implement anomaly detection API endpoint"))
    
    blocks.append(create_toggle_block("Days 5-7: Anomaly Detection UI"))
    blocks.append(create_bulleted_list_item("☐ Build anomaly detection UI dashboard"))
    blocks.append(create_bulleted_list_item("☐ Test with REAL anomalies from your AWS account"))
    
    blocks.append(create_divider())
    
    # 4. Week 2
    blocks.append(create_heading_block("📅 Week 2: Right-Sizing & CloudWatch Integration", 2))
    blocks.append(create_callout_block(
        "Goal: Deploy intelligent right-sizing recommendations with specific savings ($X/month)",
        icon="💰",
        color="orange"
    ))
    
    blocks.append(create_toggle_block("Days 1-2: CloudWatch Metrics Collection"))
    blocks.append(create_bulleted_list_item("☐ Collect REAL EC2 CloudWatch metrics (CPU, memory, network)"))
    blocks.append(create_bulleted_list_item("☐ Store metrics in database"))
    
    blocks.append(create_toggle_block("Days 3-4: Right-Sizing Model"))
    blocks.append(create_bulleted_list_item("☐ Train K-means clustering model"))
    blocks.append(create_bulleted_list_item("☐ Implement right-sizing recommendation engine"))
    blocks.append(create_bulleted_list_item("☐ Calculate specific savings (e.g., 'Save $73/month')"))
    
    blocks.append(create_toggle_block("Days 5-7: Right-Sizing UI"))
    blocks.append(create_bulleted_list_item("☐ Build right-sizing recommendation UI"))
    blocks.append(create_bulleted_list_item("☐ Show 'Apply Recommendation' flow"))
    
    blocks.append(create_divider())
    
    # 5. Week 3
    blocks.append(create_heading_block("📅 Week 3: Forecasting & Polish", 2))
    blocks.append(create_callout_block(
        "Goal: Complete ML features and polish for presentation",
        icon="✨",
        color="pink"
    ))
    
    blocks.append(create_toggle_block("Days 1-2: Cost Forecasting"))
    blocks.append(create_bulleted_list_item("☐ Train Prophet/LSTM forecasting model"))
    blocks.append(create_bulleted_list_item("☐ Implement forecasting API endpoint"))
    blocks.append(create_bulleted_list_item("☐ Build forecasting dashboard with confidence intervals"))
    
    blocks.append(create_toggle_block("Days 3-4: UI/UX Polish"))
    blocks.append(create_bulleted_list_item("☐ Improve all ML visualizations"))
    blocks.append(create_bulleted_list_item("☐ Add loading states and error handling"))
    blocks.append(create_bulleted_list_item("☐ Mobile responsiveness"))
    
    blocks.append(create_toggle_block("Days 5-7: Presentation Prep"))
    blocks.append(create_bulleted_list_item("☐ Presentation preparation"))
    
    blocks.append(create_divider())
    
    # 6. Critical Requirements
    blocks.append(create_heading_block("⚠️ Critical Requirements", 2))
    blocks.append(create_callout_block(
        "ALL implementations must use REAL data only. NO mock or demo data allowed!",
        icon="🚨",
        color="red"
    ))
    
    blocks.append(create_bulleted_list_item("✅ Use REAL AWS CUR data for training (minimum 90 days)"))
    blocks.append(create_bulleted_list_item("✅ Collect REAL CloudWatch metrics (CPU, memory, network)"))
    blocks.append(create_bulleted_list_item("✅ Train models on REAL historical patterns"))
    blocks.append(create_bulleted_list_item("✅ Test with REAL anomalies from your AWS account"))
    blocks.append(create_bulleted_list_item("✅ Show REAL right-sizing recommendations with actual savings"))
    blocks.append(create_bulleted_list_item("✅ Forecast using REAL cost trends"))
    
    blocks.append(create_divider())
    
    # 7. Success Metrics
    blocks.append(create_heading_block("🎯 Success Metrics", 2))
    blocks.append(create_quote("Demonstrate these in your presentation:"))
    
    blocks.append(create_numbered_list_item("Find at least 1 REAL anomaly in your AWS account"))
    blocks.append(create_numbered_list_item("Show 1 right-sizing recommendation with specific savings ($X/month)"))
    blocks.append(create_numbered_list_item("Display 30-day cost forecast with confidence intervals"))
    blocks.append(create_numbered_list_item("All models trained on REAL AWS data (not mock)"))
    
    blocks.append(create_divider())
    
    # 8. Daily Progress Tracker
    blocks.append(create_heading_block("📝 Daily Progress Tracker", 2))
    blocks.append(create_callout_block(
        "Update this section daily with what you completed",
        icon="📅",
        color="yellow"
    ))
    
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    blocks.append(create_heading_block(f"Today: {today}", 3))
    blocks.append(create_paragraph("What I completed today:"))
    blocks.append(create_bulleted_list_item("• "))
    blocks.append(create_paragraph("What I'm working on tomorrow:"))
    blocks.append(create_bulleted_list_item("• "))
    blocks.append(create_paragraph("Blockers/Issues:"))
    blocks.append(create_bulleted_list_item("• None"))
    
    blocks.append(create_divider())
    
    # 9. Resources
    blocks.append(create_heading_block("🔗 Resources & Links", 2))
    blocks.append(create_paragraph("Important documentation:"))
    blocks.append(create_bulleted_list_item("ML Cost Optimization Roadmap"))
    blocks.append(create_bulleted_list_item("ML Models Implementation Plan"))
    blocks.append(create_bulleted_list_item("Production Requirements (REAL DATA ONLY)"))
    blocks.append(create_bulleted_list_item("World-Class Engineer Recommendations"))
    
    blocks.append(create_divider())
    
    # 10. Notes
    blocks.append(create_heading_block("💡 Notes", 2))
    blocks.append(create_callout_block(
        "Remember: ML features differentiate you from competitors. Focus on Anomaly Detection first, then Right-Sizing, then Forecasting.",
        icon="💭",
        color="gray"
    ))
    
    # Add blocks to page
    print(f"\n📝 Adding {len(blocks)} formatted blocks...")
    
    try:
        batch_size = 100
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            notion.blocks.children.append(
                block_id=page_id,
                children=batch
            )
            print(f"✅ Added blocks {i+1}-{min(i+batch_size, len(blocks))}")
        
        print("\n✅ Beautiful formatting complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding blocks: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Clear & Format Notion Page")
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
        sys.exit(1)
    
    # Clear existing content
    if clear_page_blocks(PAGE_ID):
        # Add beautiful formatting
        if format_page_beautifully(PAGE_ID):
            print("\n🎉 Done! Your Notion page is now beautifully formatted!")
            print("\n💡 Refresh your browser to see the changes!")
        else:
            print("\n❌ Failed to add formatting")
    else:
        print("\n❌ Failed to clear page")


