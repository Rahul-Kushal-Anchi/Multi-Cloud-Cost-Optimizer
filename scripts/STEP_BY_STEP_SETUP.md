# 📋 Step-by-Step: Notion Automation Setup

## 🎯 **Goal:** Automate your Notion task tracker setup

---

## **STEP 1: Install Python Dependencies** (2 minutes)

### **Check if Python is installed:**
```bash
python3 --version
```
Should show: `Python 3.x.x`

### **Install Notion Python library:**
```bash
pip3 install notion-client
```

**If you get permission errors:**
```bash
pip3 install --user notion-client
```

**Verify installation:**
```bash
python3 -c "import notion_client; print('✅ Notion client installed')"
```

---

## **STEP 2: Verify Your Credentials** (1 minute)

### **Check if .env file exists:**
```bash
cd /Users/rahulkushalanchi/Downloads/multi-cloud-cost-optimizer
ls -la scripts/.env
```

**If it exists, you're good!** ✅  
**If not, create it:**
```bash
cat > scripts/.env << 'EOF'
NOTION_TOKEN=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
NOTION_USER_ID=22dd872b-594c-814c-84b8-0002da5d3d3f
EOF
```

---

## **STEP 3: Share Your Notion Page with Integration** (3 minutes)

### **3.1: Open Your Notion Page**
1. Go to [notion.so](https://notion.so)
2. Open your **"Final Exam Prep"** page (or the page where you pasted the task tracker)

### **3.2: Add Integration Connection**
1. Click **"..."** (three dots) in the top right
2. Click **"Add connections"** or **"Connections"**
3. Search for: **"Cost Optimizer Tracker"** (or your integration name)
4. If you don't see it, create it:
   - Go to: https://www.notion.so/my-integrations
   - Click **"+ New integration"**
   - Name: **"Cost Optimizer Tracker"**
   - Select your workspace
   - Click **"Submit"**
   - Copy the token (starts with `secret_` or `ntn_`)

### **3.3: Connect Integration to Page**
1. Back on your Notion page
2. Click **"..."** → **"Add connections"**
3. Select **"Cost Optimizer Tracker"**
4. Make sure it has **"Edit"** permissions
5. Click **"Confirm"**

**✅ Done!** Your page is now connected.

---

## **STEP 4: Get Your Page ID** (1 minute)

### **Method 1: From Notion URL**
1. Open your Notion page
2. Click **"..."** → **"Copy link"**
3. The URL looks like:
   ```
   https://www.notion.so/Final-Exam-Prep-abc123def456ghi789jkl012
   ```
4. Copy the part after the last `/` and before any `?`
   - Example: `abc123def456ghi789jkl012`
   - This is your **Page ID**

### **Method 2: Let Script Find It**
- The script can list your pages and help you find it
- Just run the script without a page ID

---

## **STEP 5: Run the Automation Script** (2 minutes)

### **Option A: Use Convenience Script (Easiest)**
```bash
cd /Users/rahulkushalanchi/Downloads/multi-cloud-cost-optimizer
./scripts/run_notion_automation.sh
```

### **Option B: Run Python Script Directly**
```bash
cd /Users/rahulkushalanchi/Downloads/multi-cloud-cost-optimizer
export NOTION_TOKEN="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"
export NOTION_USER_ID="22dd872b-594c-814c-84b8-0002da5d3d3f"
python3 scripts/notion_automation.py
```

### **Option C: With Page ID**
```bash
./scripts/run_notion_automation.sh YOUR_PAGE_ID_HERE
```

---

## **STEP 6: Follow Script Prompts** (5 minutes)

### **What the script will do:**

1. **Connect to Notion** ✅
   - Verifies your token works
   - Connects to your account

2. **List Your Pages** 📄
   - Shows all pages you have access to
   - Helps you find your task tracker page

3. **Find Your Page** 🔍
   - If you provide page ID: Uses it directly
   - If not: Lists pages and asks you to choose

4. **Create Database Structure** 📊
   - Creates a database for tasks
   - Adds properties: Status, Week, Due Date, Priority
   - Sets up views

5. **Done!** ✅
   - Your Notion page is now organized
   - Database structure is ready

---

## **STEP 7: Manual Steps (If Needed)** (5 minutes)

### **Convert Checkboxes:**
Since Notion API can't convert markdown checkboxes automatically:

1. **Open your Notion page**
2. **Select all `- [ ]` text**
3. **Type `/checkbox`** or click checkbox button
4. **Done!** All checkboxes converted

### **Import Tasks to Database:**
1. **Open the database** created by the script
2. **Copy tasks** from `docs/notion/NOTION_IMPORT_READY.md`
3. **Paste into database** (or add manually)
4. **Fill in properties:** Status, Week, Due Date, Priority

---

## **STEP 8: Set Up Views** (3 minutes)

### **Create These Views:**

1. **"All Tasks"** (Default)
   - Shows all tasks

2. **"This Week"**
   - Filter: Week = Week 1
   - Update weekly

3. **"By Status"**
   - Group by: Status
   - See what's done vs pending

4. **"By Priority"**
   - Group by: Priority
   - Focus on critical tasks

5. **"Due This Week"**
   - Filter: Due Date is this week
   - See urgent deadlines

---

## **STEP 9: Set Reminders** (2 minutes)

### **For Important Tasks:**

1. **Click on a task**
2. **Click the date** (Due Date property)
3. **Set reminder:** "1 day before due date"
4. **Save**

### **Important Dates to Set Reminders:**
- ✅ Nov 26, 2025 - Infrastructure Setup due
- ✅ Nov 28, 2025 - Anomaly Detection Model due
- ✅ Dec 1, 2025 - Anomaly Detection UI due
- ✅ Dec 4, 2025 - Right-Sizing Model due
- ✅ Dec 6, 2025 - Right-Sizing API due
- ✅ Dec 8, 2025 - Right-Sizing UI due
- ✅ Dec 10, 2025 - Cost Forecasting due
- ✅ Dec 12, 2025 - UI/UX Polish due
- ✅ Dec 13, 2025 - **PRESENTATION DAY** 🔴

---

## **STEP 10: Start Tracking!** (Ongoing)

### **Daily Workflow:**

**Morning:**
- Open Notion
- Review today's tasks
- Check off completed tasks

**During Work:**
- Update task status: Not Started → In Progress → Complete
- Add notes to tasks
- Check "Real Data Verified" when done

**Evening:**
- Review completed tasks
- Update progress metrics
- Plan tomorrow

---

## ✅ **Complete Checklist**

- [ ] Python dependencies installed
- [ ] Credentials saved in `scripts/.env`
- [ ] Notion integration created
- [ ] Page shared with integration
- [ ] Page ID obtained
- [ ] Automation script run
- [ ] Database structure created
- [ ] Checkboxes converted (manual)
- [ ] Tasks imported to database
- [ ] Views created
- [ ] Reminders set
- [ ] Ready to track progress!

---

## 🆘 **Troubleshooting**

### **Error: "NOTION_TOKEN not set"**
```bash
# Make sure .env file exists
ls -la scripts/.env

# Or set manually
export NOTION_TOKEN="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"
```

### **Error: "Cannot access page"**
- Make sure page is shared with integration
- Check integration has "Edit" permissions
- Verify page ID is correct

### **Error: "No pages found"**
- Make sure integration is added to workspace
- Check integration has access to pages
- Try creating a new integration

### **Error: "Module not found: notion_client"**
```bash
pip3 install notion-client
```

---

## 🎯 **Quick Reference**

**Run automation:**
```bash
./scripts/run_notion_automation.sh
```

**Your credentials:**
- Token: `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`
- User ID: `22dd872b-594c-814c-84b8-0002da5d3d3f`
- Stored in: `scripts/.env` (local only)

**Your task tracker:**
- File: `docs/notion/NOTION_IMPORT_READY.md`
- Ready to paste into Notion

---

## 🚀 **You're Ready!**

Just follow these steps in order, and you'll have your Notion automation set up in about 15 minutes!

**Start with Step 1 and work through each step.** ✅

