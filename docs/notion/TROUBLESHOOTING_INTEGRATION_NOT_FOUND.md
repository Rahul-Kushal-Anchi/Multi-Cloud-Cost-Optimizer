# 🔍 Troubleshooting: Integration Not Found

## ❌ **Problem: Integration doesn't appear when searching**

You see the "Invite" dialog, but when you search for "Cost Optimizer Tracker", it doesn't show up.

---

## ✅ **Solution 1: Check Integration Name**

The integration name must match **exactly**.

1. Go to https://www.notion.so/my-integrations
2. Find your integration
3. **Check the exact name** (it might be different!)
   - Could be: "My Integration"
   - Could be: "Cost Optimizer Tracker"
   - Could be: Something else you named it

4. **Copy the exact name** and search for it in the Invite dialog

---

## ✅ **Solution 2: Verify Integration Exists**

1. Go to https://www.notion.so/my-integrations
2. Make sure you see your integration listed
3. If not, create a new one:
   - Click "+ New integration"
   - Name it: "Cost Optimizer Tracker"
   - Select your workspace
   - Click "Submit"
   - Copy the token (starts with `secret_`)

---

## ✅ **Solution 3: Check Workspace**

The integration must be in the **same workspace** as your page.

1. Check which workspace your page is in
2. Check which workspace your integration is in
3. They must match!

**To fix:**
- Create a new integration in the correct workspace
- Or move your page to the integration's workspace

---

## ✅ **Solution 4: Try Different Search Terms**

Sometimes Notion's search is picky:

1. Try searching for just "Cost"
2. Try searching for just "Optimizer"
3. Try searching for just "Tracker"
4. Try typing the first few letters slowly

---

## ✅ **Solution 5: Refresh and Retry**

1. **Close the Invite dialog**
2. **Refresh the Notion page** (F5 or Cmd+R)
3. **Click "Share" again**
4. **Try searching again**

---

## ✅ **Solution 6: Use Integration Token Directly**

If the integration still doesn't appear, you can try:

1. Go to https://www.notion.so/my-integrations
2. Click on your integration
3. Copy the **Internal Integration Token**
4. Make sure it's in your `scripts/.env` file:
   ```
   NOTION_TOKEN=secret_your_token_here
   ```

5. The script should still work even if you can't find it in the search!

---

## ✅ **Solution 7: Create New Integration**

If nothing works, create a fresh integration:

1. Go to https://www.notion.so/my-integrations
2. Click "+ New integration"
3. Name it: **"Cost Optimizer"** (simpler name)
4. Select your workspace
5. Click "Submit"
6. Copy the token
7. Update `scripts/.env` with the new token
8. Try searching for "Cost Optimizer" in the Invite dialog

---

## 🚀 **Alternative: Skip Sharing (Advanced)**

If you absolutely can't find the integration, you can try:

1. Make the page **public** (temporarily)
   - Click "Share" → "Settings" → Make it public
   - Run the script
   - Then make it private again

2. Or use a **workspace-level integration** (if you have admin access)

---

## 💡 **Most Common Issue**

**90% of the time**, the issue is:
- Integration name doesn't match exactly
- Integration is in a different workspace

**Quick fix:**
1. Check exact name at https://www.notion.so/my-integrations
2. Make sure workspace matches
3. Try searching with exact name

---

## 🎯 **What to Do Right Now**

1. **Go to:** https://www.notion.so/my-integrations
2. **Check:** What's the exact name of your integration?
3. **Tell me:** What name do you see?

Then we can troubleshoot from there!

---

**Need more help?** Share what you see at the integrations page!


