# 🚀 Quick Start: Use Your Page ID

## ✅ **Your Page ID**

From your Notion link:
```
https://www.notion.so/2898d3b7800c805f865bf5d8d26c9d0a?source=copy_link
```

**Page ID:** `2898d3b7800c805f865bf5d8d26c9d0a`

---

## ⚠️ **IMPORTANT: Share Page First!**

Before running the script, you **MUST** share this page with your integration:

1. Open the page: https://www.notion.so/2898d3b7800c805f865bf5d8d26c9d0a
2. Click **"Share"** (top right)
3. Click **"Add people, emails, groups, or integrations"**
4. Search for your integration name
5. Add it with **"Edit"** permissions
6. Click **"Invite"**

**Without sharing, the script won't be able to access the page!**

---

## 🚀 **Run the Script**

### **Option 1: Interactive Mode**
```bash
./scripts/QUICK_RUN.sh
```
When prompted, paste: `2898d3b7800c805f865bf5d8d26c9d0a`

### **Option 2: Direct Command**
```bash
python3 scripts/notion_automation.py 2898d3b7800c805f865bf5d8d26c9d0a
```

### **Option 3: With Environment Variables**
```bash
cd scripts
source .env
cd ..
python3 scripts/notion_automation.py 2898d3b7800c805f865bf5d8d26c9d0a
```

---

## ✅ **What Happens Next**

1. Script connects to your Notion page
2. Verifies access (make sure you shared it!)
3. Creates database structure
4. Sets up task tracker
5. Ready to use!

---

## 🔍 **Troubleshooting**

### **Error: "Cannot access page"**
- ✅ Make sure you shared the page with the integration
- ✅ Check that permissions are set to "Edit"
- ✅ Verify the Page ID is correct

### **Error: "Page not found"**
- ✅ Check the URL is correct
- ✅ Make sure the page exists
- ✅ Verify you're logged into Notion

---

## 📖 **Full Guide**

See: `docs/notion/HOW_TO_SHARE_PAGE_WITH_INTEGRATION.md`

---

**Ready?** Share the page first, then run the script! 🎉


