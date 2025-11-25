# 🚀 Quick Start - Notion Automation

## **Your Credentials:**

**Set these before running (use your actual token):**

```bash
export NOTION_TOKEN="your_notion_token_here"
export NOTION_USER_ID="your_user_id_here"
```

---

## **Option 1: Quick Run (Easiest)**

```bash
# Set credentials (replace with your actual values)
export NOTION_TOKEN="your_notion_token_here"
export NOTION_USER_ID="your_user_id_here"

# Run automation
./scripts/run_notion_automation.sh
```

---

## **Option 2: Create .env File (Recommended)**

1. **Create file:** `scripts/.env`
2. **Add your credentials:**
   ```
   NOTION_TOKEN=your_notion_token_here
   NOTION_USER_ID=your_user_id_here
   ```
3. **Run:**
   ```bash
   ./scripts/run_notion_automation.sh
   ```

**Note:** `.env` files are already in `.gitignore` - your secrets are safe!

---

## **Option 3: Direct Python**

```bash
export NOTION_TOKEN="your_notion_token_here"
python3 scripts/notion_automation.py
```

---

## **What It Does:**

1. ✅ Connects to your Notion account
2. ✅ Lists your pages
3. ✅ Helps you find your task tracker page
4. ✅ Creates database structure
5. ✅ Sets up properties and views

---

## **Next Steps:**

1. **Share your page with integration:**
   - Open Notion page
   - Click "..." → "Add connections"
   - Add "Cost Optimizer Tracker" integration

2. **Run the script:**
   ```bash
   ./scripts/run_notion_automation.sh
   ```

3. **Follow the prompts!**

---

**Ready to go!** 🚀

