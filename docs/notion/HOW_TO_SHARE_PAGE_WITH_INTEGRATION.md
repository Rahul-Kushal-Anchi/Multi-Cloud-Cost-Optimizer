# 🔐 How to Share Notion Page with Integration

## ⚠️ **Why You're Seeing "0 Pages Found"**

Notion integrations are **secure by default**. Even with a valid API token, the integration can only access pages that are **explicitly shared** with it.

**The API token alone is NOT enough!** You must share each page individually.

---

## ✅ **Step-by-Step: Share Page with Integration**

### **Step 1: Find Your Integration Name**

1. Go to https://www.notion.so/my-integrations
2. Find your integration (the one you created for the token)
3. **Note the exact name** (e.g., "Cost Optimizer Tracker" or "My Integration")

---

### **Step 2: Open Your Notion Page**

1. Open the page you want to automate (e.g., "Final Exam Prep")
2. Make sure you're logged into Notion

---

### **Step 3: Share the Page**

1. Click **"Share"** button (top right corner)
   - Or click **"..."** (three dots) → **"Share"**

2. Click **"Add people, emails, groups, or integrations"**

3. In the search box, type your **integration name**
   - Example: "Cost Optimizer Tracker"
   - It should appear in the dropdown

4. Click on your integration name

5. Set permissions to **"Edit"** (or "Full access")
   - The integration needs edit access to create databases and modify content

6. Click **"Invite"** or **"Add"**

---

### **Step 4: Verify Access**

1. The integration should now appear in the "Shared with" list
2. You should see your integration name with "Edit" permissions

---

### **Step 5: Get the Page ID**

1. While on the page, click **"..."** (three dots) → **"Copy link"**
   - Or click **"Share"** → **"Copy link"**

2. The link looks like:
   ```
   https://www.notion.so/Final-Exam-Prep-abc123def456ghi789jkl012mno345pqr678
   ```

3. **Extract the Page ID:**
   - It's the part after the last `/` and before any `?`
   - Remove hyphens: `abc123def456ghi789jkl012mno345pqr678`
   - Or keep it with hyphens: `abc123def-456ghi-789jkl-012mno-345pqr678`
   - **Both formats work!**

**Example:**
```
Link: https://www.notion.so/Final-Exam-Prep-abc123def456ghi789
Page ID: abc123def456ghi789
```

---

## 🚀 **Now Run the Script**

After sharing the page:

```bash
./scripts/QUICK_RUN.sh
```

When prompted for Page ID, paste the ID you copied.

---

## 🔍 **Troubleshooting**

### **Problem: Integration doesn't appear in search**

**Solution:**
1. Make sure you're searching for the **exact integration name**
2. Check https://www.notion.so/my-integrations to verify the name
3. Try typing just the first few letters
4. Make sure the integration is in the same workspace

---

### **Problem: "Cannot access page" error**

**Solution:**
1. Verify the page is shared with the integration
2. Check that permissions are set to "Edit" or "Full access"
3. Make sure you copied the correct Page ID
4. Try refreshing the page in Notion

---

### **Problem: Still seeing "0 pages found"**

**Solution:**
1. **Share a page first** - The script searches for pages, but if none are shared, it finds 0
2. You can skip the search and provide the Page ID directly
3. Make sure you're using the correct integration token

---

## 📋 **Quick Checklist**

- [ ] Integration created at https://www.notion.so/my-integrations
- [ ] Integration token copied to `scripts/.env`
- [ ] Page opened in Notion
- [ ] Page shared with integration (Share → Add integration → Edit permissions)
- [ ] Page ID copied from "Copy link"
- [ ] Script run with Page ID

---

## 💡 **Pro Tip: Share Multiple Pages**

If you want to automate multiple pages:

1. Share each page individually with the integration
2. Run the script for each page ID
3. Or create a parent page and share that (child pages inherit access)

---

## 🔒 **Security Note**

- ✅ Sharing a page with an integration is **safe**
- ✅ You can revoke access anytime
- ✅ The integration only sees pages you explicitly share
- ✅ Your other pages remain private

---

## 🎯 **What Happens After Sharing?**

Once you share a page and provide the Page ID:

1. ✅ Script connects to your page
2. ✅ Creates database structure
3. ✅ Sets up views and properties
4. ✅ Organizes your tasks
5. ✅ Ready to track your progress!

---

**Need help?** Check the error message in the terminal - it will tell you exactly what's wrong!

