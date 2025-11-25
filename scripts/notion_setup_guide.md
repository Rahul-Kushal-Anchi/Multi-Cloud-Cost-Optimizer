# 🤖 Notion Automation Setup Guide

## ✅ **Your Credentials**

**Set these as environment variables before running:**

```bash
export NOTION_TOKEN="your_notion_token_here"
export NOTION_USER_ID="your_user_id_here"
```

**Or create a `.env` file** (already in .gitignore):
```bash
NOTION_TOKEN=your_notion_token_here
NOTION_USER_ID=your_user_id_here
```

---

## 🚀 **Quick Setup**

### **Step 1: Install Notion Python Library**

```bash
pip install notion-client
```

### **Step 2: Get Your Page ID**

1. Open your Notion page (Final Exam Prep)
2. Click **"..."** (three dots) → **"Copy link"**
3. The link looks like: `https://www.notion.so/Final-Exam-Prep-abc123def456...`
4. Copy the part after the last `/` (the page ID)

**Example:**
```
Link: https://www.notion.so/Final-Exam-Prep-abc123def456ghi789
Page ID: abc123def456ghi789
```

### **Step 3: Share Page with Integration**

1. Open your Notion page
2. Click **"..."** → **"Add connections"**
3. Search for your integration: **"Cost Optimizer Tracker"**
4. Click to add it
5. Make sure it has **"Edit"** permissions

### **Step 4: Run Automation**

```bash
cd /Users/rahulkushalanchi/Downloads/multi-cloud-cost-optimizer
python scripts/notion_automation.py <YOUR_PAGE_ID>
```

**Or let the script find it:**

```bash
python scripts/notion_automation.py
```

---

## 🔧 **What the Script Does**

1. ✅ Connects to your Notion account
2. ✅ Lists your pages
3. ✅ Creates database structure
4. ✅ Sets up properties (Status, Week, Due Date, Priority)
5. ✅ Creates views (All Tasks, This Week, By Status)

---

## ⚠️ **Important Notes**

### **Notion API Limitations:**

- ❌ Cannot directly convert markdown `- [ ]` to Notion checkboxes
- ✅ Can create database structure
- ✅ Can create properties and views
- ✅ Can add tasks programmatically

### **Manual Steps Required:**

1. **Convert Checkboxes:**
   - Select `- [ ]` text in Notion
   - Type `/checkbox` or use checkbox button
   - Convert manually (takes 2-3 minutes)

2. **Import Tasks:**
   - Copy tasks from `docs/notion/NOTION_IMPORT_READY.md`
   - Paste into database
   - Or add tasks one by one

---

## 🎯 **Alternative: Use Notion's Built-in Features**

Since Notion API has limitations, here's the **easiest approach**:

### **Method 1: Manual Setup (5 minutes)**

1. **Paste content** from `docs/notion/NOTION_IMPORT_READY.md` into Notion
2. **Convert checkboxes:**
   - Select all `- [ ]`
   - Type `/checkbox`
   - Done!

3. **Create database** (optional):
   - Select tasks
   - Type `/turn into` → `Database`
   - Add properties: Status, Week, Due Date, Priority

### **Method 2: Use Script for Database Structure**

1. **Run script** to create database structure
2. **Manually add tasks** to the database
3. **Set up views** using Notion UI

---

## 📋 **Script Usage**

```bash
# Option 1: Let script find your page
python scripts/notion_automation.py

# Option 2: Provide page ID directly
python scripts/notion_automation.py abc123def456ghi789
```

---

## 🔒 **Security**

- ✅ Token is stored in script (local only)
- ✅ Never commit token to Git (already in .gitignore)
- ✅ You can revoke access anytime from Notion settings
- ✅ Script runs locally on your machine

---

## 🆘 **Troubleshooting**

### **Error: "Cannot access page"**
- Make sure page is shared with integration
- Check integration has "Edit" permissions

### **Error: "No pages found"**
- Make sure integration is added to workspace
- Check integration has access to pages

### **Error: "Invalid token"**
- Verify token is correct
- Check token hasn't expired
- Regenerate token if needed

---

## ✅ **Ready to Run!**

Just run:
```bash
python scripts/notion_automation.py
```

The script will guide you through the rest! 🚀

