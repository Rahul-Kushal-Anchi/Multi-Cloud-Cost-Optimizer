# 🚀 Notion Automation Setup - Your Credentials

## ✅ **Your Credentials (Set These Locally)**

Your Notion credentials are saved in `scripts/.env` (local file, not in Git).

**To use the automation:**

```bash
# Option 1: Use the convenience script (loads from .env automatically)
./scripts/run_notion_automation.sh

# Option 2: Set environment variables manually
export NOTION_TOKEN="your_notion_token_here"
export NOTION_USER_ID="22dd872b-594c-814c-84b8-0002da5d3d3f"
python3 scripts/notion_automation.py
```

---

## 📋 **Quick Start**

1. **Your `.env` file is already created** with your credentials
2. **Run:**
   ```bash
   ./scripts/run_notion_automation.sh
   ```
3. **Follow the prompts!**

---

## 🔒 **Security**

- ✅ Credentials stored in `scripts/.env` (gitignored)
- ✅ Never committed to Git
- ✅ Safe to use locally

---

**Ready to automate your Notion setup!** 🎉

