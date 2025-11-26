#!/usr/bin/env python3
"""
Create a Beautiful, Colorful Notion Page
Removes duplicates and adds vibrant colors and styling
"""

import os
import sys
from notion_client import Client
from datetime import datetime

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
    sys.exit(1)

notion = Client(auth=NOTION_TOKEN)

def clear_all_blocks(page_id):
    """Clear ALL blocks from the page"""
    print("🧹 Clearing ALL existing content...")
    
    try:
        all_blocks = []
        cursor = None
        
        while True:
            if cursor:
                response = notion.blocks.children.list(block_id=page_id, start_cursor=cursor)
            else:
                response = notion.blocks.children.list(block_id=page_id)
            
            blocks = response.get('results', [])
            all_blocks.extend(blocks)
            
            if not response.get('has_more'):
                break
            cursor = response.get('next_cursor')
        
        if not all_blocks:
            print("✅ Page is already empty")
            return True
        
        print(f"📄 Found {len(all_blocks)} blocks to remove...")
        
        # Delete all blocks
        for i, block in enumerate(all_blocks, 1):
            try:
                notion.blocks.delete(block_id=block['id'])
                if i % 20 == 0:
                    print(f"   Removed {i}/{len(all_blocks)} blocks...")
            except Exception as e:
                print(f"   ⚠️  Could not remove block {i}: {e}")
        
        print(f"✅ Cleared {len(all_blocks)} blocks")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing page: {e}")
        return False

def create_heading(text, level=1):
    return {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def create_callout(text, icon="💡", color="blue"):
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
    return {"object": "block", "type": "divider", "divider": {}}

def create_toggle(title):
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": title}}]
        }
    }

def create_bullet(text):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def create_numbered(text):
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def create_quote(text):
    return {
        "object": "block",
        "type": "quote",
        "quote": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def create_paragraph(text):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def format_colorful_page(page_id):
    """Create a beautiful, colorful Notion page"""
    print("\n🎨 Creating colorful, beautiful page...")
    print("=" * 60)
    
    blocks = []
    
    # 1. HERO SECTION - Large colorful header
    blocks.append(create_heading("🚀 Final Exam Preparation - ML Cost Optimizer", 1))
    blocks.append(create_callout(
        "Complete your ML-powered cost optimization platform by December 13, 2025. Track your progress daily and ensure all features use REAL data only.",
        icon="🎯",
        color="blue"
    ))
    blocks.append(create_divider())
    
    # 2. PROGRESS TRACKER - Green callout
    blocks.append(create_heading("📊 Progress Tracker", 2))
    blocks.append(create_callout(
        "📈 Total Tasks: 27 | ✅ Completed: 0 | 🔄 In Progress: 0 | ⬜ Not Started: 27 | 📊 Overall: 0%",
        icon="📈",
        color="green"
    ))
    blocks.append(create_divider())
    
    # 3. WEEK 1 - Purple theme
    blocks.append(create_heading("📅 Week 1: ML Foundation & Anomaly Detection", 2))
    blocks.append(create_callout(
        "Goal: Deploy ML-powered anomaly detection using REAL AWS CUR data",
        icon="🔍",
        color="purple"
    ))
    
    blocks.append(create_toggle("📦 Days 1-2: Infrastructure Setup"))
    blocks.append(create_bullet("☐ Set up ML training environment (scikit-learn, pandas, numpy)"))
    blocks.append(create_bullet("☐ Create api/ml/ directory structure"))
    blocks.append(create_bullet("☐ Set up CloudWatch metrics collection (REAL data only)"))
    
    blocks.append(create_toggle("🤖 Days 3-4: Anomaly Detection Model"))
    blocks.append(create_bullet("☐ Train Isolation Forest model on REAL AWS CUR data (90 days)"))
    blocks.append(create_bullet("☐ Implement anomaly detection API endpoint"))
    
    blocks.append(create_toggle("🎨 Days 5-7: Anomaly Detection UI"))
    blocks.append(create_bullet("☐ Build anomaly detection UI dashboard"))
    blocks.append(create_bullet("☐ Create anomaly detail modal/page"))
    blocks.append(create_bullet("☐ Show root cause analysis"))
    blocks.append(create_bullet("☐ Show affected services"))
    blocks.append(create_bullet("☐ Show cost impact"))
    blocks.append(create_bullet("☐ Show anomaly trend chart"))
    blocks.append(create_bullet("☐ Test with real data"))
    
    blocks.append(create_divider())
    
    # 4. WEEK 2 - Orange theme
    blocks.append(create_heading("📅 Week 2: Right-Sizing & CloudWatch Integration", 2))
    blocks.append(create_callout(
        "Goal: Deploy intelligent right-sizing recommendations with specific savings ($X/month)",
        icon="💰",
        color="orange"
    ))
    
    blocks.append(create_toggle("📊 Days 1-2: CloudWatch Metrics Collection"))
    blocks.append(create_bullet("☐ Collect REAL EC2 CloudWatch metrics (CPU, memory, network)"))
    blocks.append(create_bullet("☐ Store metrics in database"))
    blocks.append(create_bullet("☐ Verify metrics are real (check timestamps, values)"))
    blocks.append(create_bullet("☐ **NO MOCK METRICS** - all must be queried from real CloudWatch"))
    
    blocks.append(create_toggle("🧠 Days 3-4: Right-Sizing Model"))
    blocks.append(create_bullet("☐ Create api/ml/right_sizing.py"))
    blocks.append(create_bullet("☐ Implement instance analysis logic using REAL CloudWatch metrics"))
    blocks.append(create_bullet("☐ Calculate required resources from REAL usage patterns"))
    blocks.append(create_bullet("☐ Match REAL instances to optimal size"))
    blocks.append(create_bullet("☐ Calculate savings using REAL AWS pricing"))
    blocks.append(create_bullet("☐ Implement risk level calculation"))
    blocks.append(create_bullet("☐ Calculate confidence scores"))
    blocks.append(create_bullet("☐ Generate reasoning text"))
    blocks.append(create_bullet("☐ Test model with real instances"))
    
    blocks.append(create_toggle("🔌 Days 4-5: Right-Sizing API"))
    blocks.append(create_bullet("☐ Create api/routers/ml_right_sizing.py"))
    blocks.append(create_bullet("☐ Implement GET /api/ml/right-sizing endpoint"))
    blocks.append(create_bullet("☐ Fetch REAL EC2 instances from AWS using boto3"))
    blocks.append(create_bullet("☐ Get REAL CloudWatch metrics for each instance"))
    blocks.append(create_bullet("☐ Generate recommendations from REAL analysis"))
    blocks.append(create_bullet("☐ Return formatted recommendations with REAL data"))
    blocks.append(create_bullet("☐ Test API with real instances"))
    
    blocks.append(create_toggle("🎨 Days 6-7: Right-Sizing UI"))
    blocks.append(create_bullet("☐ Update web-app/src/pages/Optimizations.js"))
    blocks.append(create_bullet("☐ Add ML-powered recommendations section"))
    blocks.append(create_bullet("☐ Create detailed recommendation card component"))
    blocks.append(create_bullet("☐ Show before/after comparison"))
    blocks.append(create_bullet("☐ Show utilization charts"))
    blocks.append(create_bullet("☐ Show savings breakdown"))
    blocks.append(create_bullet("☐ Create savings calculator component"))
    blocks.append(create_bullet("☐ Add 'Apply Recommendation' button"))
    blocks.append(create_bullet("☐ Test with real recommendations"))
    
    blocks.append(create_divider())
    
    # 5. WEEK 3 - Pink theme
    blocks.append(create_heading("📅 Week 3: Forecasting & Polish", 2))
    blocks.append(create_callout(
        "Goal: Complete ML features and polish for presentation",
        icon="✨",
        color="pink"
    ))
    
    blocks.append(create_toggle("📈 Days 1-2: Cost Forecasting"))
    blocks.append(create_bullet("☐ Create api/ml/forecasting.py"))
    blocks.append(create_bullet("☐ Implement Prophet or LSTM model"))
    blocks.append(create_bullet("☐ Query REAL historical cost data from CUR (12 months minimum)"))
    blocks.append(create_bullet("☐ Train on REAL historical costs"))
    blocks.append(create_bullet("☐ Generate forecasts from REAL model predictions (3, 6, 12 months)"))
    blocks.append(create_bullet("☐ Calculate confidence intervals from REAL model uncertainty"))
    blocks.append(create_bullet("☐ Create api/routers/ml_forecasting.py"))
    blocks.append(create_bullet("☐ Implement GET /api/ml/forecasting endpoint"))
    blocks.append(create_bullet("☐ Create forecasting chart component"))
    blocks.append(create_bullet("☐ Show forecast line with confidence bands"))
    blocks.append(create_bullet("☐ Show trend indicators"))
    blocks.append(create_bullet("☐ Show key drivers list"))
    blocks.append(create_bullet("☐ Test with real forecasts"))
    
    blocks.append(create_toggle("🎨 Days 3-4: UI/UX Polish"))
    blocks.append(create_bullet("☐ Add ML insights section to dashboard"))
    blocks.append(create_bullet("☐ Show top anomalies widget"))
    blocks.append(create_bullet("☐ Show top recommendations widget"))
    blocks.append(create_bullet("☐ Show forecast preview"))
    blocks.append(create_bullet("☐ Enhance recommendation cards"))
    blocks.append(create_bullet("☐ Improve anomaly alerts styling"))
    blocks.append(create_bullet("☐ Add loading states"))
    blocks.append(create_bullet("☐ Add empty states"))
    blocks.append(create_bullet("☐ Improve charts and visualizations"))
    blocks.append(create_bullet("☐ Add tooltips for ML features"))
    blocks.append(create_bullet("☐ Add help text for recommendations"))
    blocks.append(create_bullet("☐ Improve navigation"))
    blocks.append(create_bullet("☐ Mobile responsiveness"))
    
    blocks.append(create_toggle("📝 Days 5-7: Presentation Prep"))
    blocks.append(create_bullet("☐ Create presentation outline"))
    blocks.append(create_bullet("☐ Design slide template"))
    blocks.append(create_bullet("☐ Create problem statement slides"))
    blocks.append(create_bullet("☐ Create solution overview slides"))
    blocks.append(create_bullet("☐ Create architecture diagram slides"))
    blocks.append(create_bullet("☐ Create feature demo slides"))
    blocks.append(create_bullet("☐ Create technical deep-dive slides"))
    blocks.append(create_bullet("☐ Create results & impact slides"))
    blocks.append(create_bullet("☐ Create future roadmap slides"))
    blocks.append(create_bullet("☐ Connect to REAL AWS account with actual cost data"))
    blocks.append(create_bullet("☐ Write presentation script showing REAL ML outputs"))
    blocks.append(create_bullet("☐ Document ML models architecture"))
    blocks.append(create_bullet("☐ Document API endpoints"))
    blocks.append(create_bullet("☐ Create architecture diagrams"))
    blocks.append(create_bullet("☐ Test all features end-to-end"))
    blocks.append(create_bullet("☐ Practice presentation (3x)"))
    blocks.append(create_bullet("☐ Prepare backup plan (if demo fails)"))
    
    blocks.append(create_divider())
    
    # 6. CRITICAL REQUIREMENTS - Red warning
    blocks.append(create_heading("⚠️ Critical Requirements", 2))
    blocks.append(create_callout(
        "🚨 ALL implementations must use REAL data only. NO mock or demo data allowed!",
        icon="🚨",
        color="red"
    ))
    
    blocks.append(create_bullet("✅ Use REAL AWS CUR data for training (minimum 90 days)"))
    blocks.append(create_bullet("✅ Collect REAL CloudWatch metrics (CPU, memory, network)"))
    blocks.append(create_bullet("✅ Train models on REAL historical patterns"))
    blocks.append(create_bullet("✅ Test with REAL anomalies from your AWS account"))
    blocks.append(create_bullet("✅ Show REAL right-sizing recommendations with actual savings"))
    blocks.append(create_bullet("✅ Forecast using REAL cost trends"))
    blocks.append(create_bullet("✅ **NO MOCK DATA** - verify all metrics, instances, and recommendations are real"))
    
    blocks.append(create_divider())
    
    # 7. SUCCESS METRICS - Yellow highlight
    blocks.append(create_heading("🎯 Success Metrics", 2))
    blocks.append(create_callout(
        "Demonstrate these in your presentation on December 13, 2025",
        icon="🎯",
        color="yellow"
    ))
    
    blocks.append(create_numbered("Find at least 1 REAL anomaly in your AWS account"))
    blocks.append(create_numbered("Show 1 right-sizing recommendation with specific savings ($X/month)"))
    blocks.append(create_numbered("Display 30-day cost forecast with confidence intervals"))
    blocks.append(create_numbered("All models trained on REAL AWS data (not mock)"))
    
    blocks.append(create_divider())
    
    # 8. VALIDATION CHECKLIST - Green theme
    blocks.append(create_heading("✅ Validation Checklist", 2))
    blocks.append(create_callout(
        "Before Presentation (Dec 13): Verify all items below",
        icon="✅",
        color="green"
    ))
    
    blocks.append(create_toggle("🔍 Anomaly Detection"))
    blocks.append(create_bullet("☐ Model trained on real cost data (check training logs)"))
    blocks.append(create_bullet("☐ Anomalies detected from real cost patterns"))
    blocks.append(create_bullet("☐ Anomaly scores are from actual ML model inference"))
    blocks.append(create_bullet("☐ Root causes identified from real CloudWatch/Athena queries"))
    
    blocks.append(create_toggle("💰 Right-Sizing"))
    blocks.append(create_bullet("☐ EC2 instances queried from real AWS account"))
    blocks.append(create_bullet("☐ CloudWatch metrics are real (verify timestamps match)"))
    blocks.append(create_bullet("☐ Recommendations based on real utilization analysis"))
    blocks.append(create_bullet("☐ Savings calculated using real AWS pricing"))
    
    blocks.append(create_toggle("📈 Forecasting"))
    blocks.append(create_bullet("☐ Model trained on real historical costs"))
    blocks.append(create_bullet("☐ Forecasts generated from real model predictions"))
    blocks.append(create_bullet("☐ Confidence intervals calculated from real model uncertainty"))
    
    blocks.append(create_toggle("🔧 General"))
    blocks.append(create_bullet("☐ No mock data files in codebase"))
    blocks.append(create_bullet("☐ No demo flags or fake data generators"))
    blocks.append(create_bullet("☐ All API endpoints return real data"))
    blocks.append(create_bullet("☐ All UI displays real information"))
    blocks.append(create_bullet("☐ All ML models use real data"))
    
    blocks.append(create_divider())
    
    # 9. DAILY PROGRESS TRACKER - Blue theme
    blocks.append(create_heading("📝 Daily Progress Tracker", 2))
    blocks.append(create_callout(
        "Update this section daily with what you completed",
        icon="📅",
        color="blue"
    ))
    
    today = datetime.now().strftime("%B %d, %Y")
    blocks.append(create_heading(f"Today: {today}", 3))
    blocks.append(create_paragraph("What I completed today:"))
    blocks.append(create_bullet("• "))
    blocks.append(create_paragraph("What I'm working on tomorrow:"))
    blocks.append(create_bullet("• "))
    blocks.append(create_paragraph("Blockers/Issues:"))
    blocks.append(create_bullet("• None"))
    
    blocks.append(create_divider())
    
    # 10. RESOURCES - Gray theme
    blocks.append(create_heading("🔗 Resources & Links", 2))
    blocks.append(create_callout(
        "Important documentation and guides",
        icon="📚",
        color="gray"
    ))
    
    blocks.append(create_bullet("📖 ML Cost Optimization Roadmap"))
    blocks.append(create_bullet("📖 ML Models Implementation Plan"))
    blocks.append(create_bullet("📖 Production Requirements (REAL DATA ONLY)"))
    blocks.append(create_bullet("📖 World-Class Engineer Recommendations"))
    blocks.append(create_bullet("📖 Multi-Cloud Strategy"))
    
    blocks.append(create_divider())
    
    # 11. FINAL NOTES - Quote style
    blocks.append(create_heading("💡 Key Reminders", 2))
    blocks.append(create_quote("ML features differentiate you from competitors. Focus on Anomaly Detection first, then Right-Sizing, then Forecasting."))
    blocks.append(create_callout(
        "Remember: Real data = Real value. No shortcuts, no mocks, no demos. Production-ready only!",
        icon="💭",
        color="purple"
    ))
    
    # Add all blocks
    print(f"\n📝 Adding {len(blocks)} colorful blocks...")
    
    try:
        batch_size = 100
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            notion.blocks.children.append(block_id=page_id, children=batch)
            print(f"✅ Added blocks {i+1}-{min(i+batch_size, len(blocks))}")
        
        print("\n✅ Beautiful colorful page created!")
        print("\n🎨 Your page now has:")
        print("   ✅ Colorful callout boxes (blue, green, purple, orange, pink, red, yellow, gray)")
        print("   ✅ Organized toggle sections")
        print("   ✅ No duplicates")
        print("   ✅ Clear structure")
        print("   ✅ Visual hierarchy")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Colorful Notion Page Creator")
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
    
    # Clear and format
    if clear_all_blocks(PAGE_ID):
        if format_colorful_page(PAGE_ID):
            print("\n🎉 Done! Your Notion page is now colorful and beautiful!")
            print("\n💡 Refresh your browser to see the changes!")
        else:
            print("\n❌ Failed to create colorful page")
    else:
        print("\n❌ Failed to clear page")


