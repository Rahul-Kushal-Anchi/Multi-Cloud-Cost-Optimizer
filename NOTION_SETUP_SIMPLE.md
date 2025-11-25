# 🚀 Notion Automation - Simple Step-by-Step

## ⚡ **QUICKEST WAY (2 minutes):**

```bash
cd /Users/rahulkushalanchi/Downloads/multi-cloud-cost-optimizer
./scripts/QUICK_RUN.sh
```

**That's it!** The script does everything automatically.

---

## 📋 **MANUAL STEP-BY-STEP (15 minutes):**

### **STEP 1: Install Python Library** ⏱️ 1 min
```bash
pip3 install notion-client
```

---

### **STEP 2: Share Your Notion Page** ⏱️ 3 min

1. **Open your Notion page** (Final Exam Prep)
2. **Click "..."** (three dots) → **"Add connections"**
3. **Search for:** "Cost Optimizer Tracker"
4. **If not found, create it:**
   - Go to: https://www.notion.so/my-integrations
   - Click **"+ New integration"**
   - Name: "Cost Optimizer Tracker"
   - Copy the token
5. **Connect it to your page** with "Edit" permissions

---

### **STEP 3: Get Your Page ID** ⏱️ 1 min

1. **Click "..."** → **"Copy link"**
2. **URL looks like:** `https://www.notion.so/Final-Exam-Prep-abc123def456...`
3. **Copy the part after last `/`:** `abc123def456` (this is your Page ID)

**Or skip this** - the script can find it for you!

---

### **STEP 4: Run Automation** ⏱️ 2 min

```bash
cd /Users/rahulkushalanchi/Downloads/multi-cloud-cost-optimizer
./scripts/run_notion_automation.sh
```

**Or with page ID:**
```bash
./scripts/run_notion_automation.sh YOUR_PAGE_ID_HERE
```

---

### **STEP 5: Follow Prompts** ⏱️ 5 min

The script will:
1. ✅ Connect to Notion
2. ✅ List your pages
3. ✅ Help you find your page
4. ✅ Create database structure
5. ✅ Set up properties and views

---

### **STEP 6: Convert Checkboxes** ⏱️ 3 min

**Manual step (Notion API limitation):**

1. **Open your Notion page**
2. **Select all `- [ ]` text**
3. **Type `/checkbox`** or click checkbox button
4. **Done!** ✅

---

### **STEP 7: Set Up Views** ⏱️ 2 min

1. **Click on database** created by script
2. **Click "..."** → **"Add a view"**
3. **Create views:**
   - "This Week" (filter: Week = Week 1)
   - "By Status" (group by: Status)
   - "By Priority" (group by: Priority)

---

## ✅ **DONE!**

Your Notion task tracker is now automated and ready to use!

---

## 🆘 **If Something Goes Wrong:**

### **Error: "NOTION_TOKEN not set"**
```bash
export NOTION_TOKEN="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"
export NOTION_USER_ID="22dd872b-594c-814c-84b8-0002da5d3d3f"
```

### **Error: "Cannot access page"**
- Make sure page is shared with integration
- Check integration has "Edit" permissions

### **Error: "Module not found"**
```bash
pip3 install notion-client
```

---

## 🎯 **Your Credentials:**

- **Token:** `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`
- **User ID:** `22dd872b-594c-814c-84b8-0002da5d3d3f`
- **Stored in:** `scripts/.env` (local only, safe!)

---

**Start with the QUICK_RUN.sh script - it's the easiest!** 🚀

