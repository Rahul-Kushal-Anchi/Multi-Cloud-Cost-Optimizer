# How to Disable Other AI Bots and Keep Only CodeRabbit

## Overview
CodeRabbit automatically skips reviews when it detects other AI code review bots to avoid duplicate reviews. To ensure CodeRabbit reviews all PRs, you need to disable other AI review bots.

## Step-by-Step Guide

### 1. Disable Macroscope App Bot

1. **Go to GitHub Repository Settings**
   - Navigate to: `https://github.com/Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer/settings`

2. **Access Installed Apps**
   - Click on **"Integrations"** in the left sidebar
   - Or go directly to: `https://github.com/Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer/settings/installations`

3. **Find Macroscope App**
   - Look for **"Macroscope"** or **"macroscopeapp"** in the list
   - Click on it

4. **Configure Access**
   - Click **"Configure"** next to your repository
   - Or click **"Uninstall"** to completely remove it
   - If configuring, uncheck **"Pull requests"** permission

5. **Save Changes**
   - Click **"Save"** or **"Uninstall"** to confirm

### 2. Disable GitHub Copilot Code Review (if enabled)

1. **Go to GitHub Settings**
   - Navigate to: `https://github.com/settings/apps`

2. **Find GitHub Copilot**
   - Look for **"GitHub Copilot"** in installed apps
   - Note: GitHub Copilot for code suggestions is different from code review
   - If there's a separate "Copilot Code Review" app, disable it

3. **Repository Settings**
   - Go to: `https://github.com/Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer/settings`
   - Click **"Integrations"**
   - Find any Copilot-related integrations
   - Disable PR review features

### 3. Check for Other AI Review Bots

Common AI code review bots to check for:
- ✅ **CodeRabbit** (keep this one!)
- ❌ **Macroscope** (disable)
- ❌ **CodeQL** (this is security scanning, can keep)
- ❌ **Dependabot** (dependency updates, can keep)
- ❌ **SonarCloud** (if installed, can disable or keep)
- ❌ **DeepSource** (if installed, can disable or keep)

**Note:** CodeQL and Dependabot are not AI review bots, so they won't interfere with CodeRabbit.

### 4. Verify CodeRabbit Configuration

Ensure `.coderabbit.yml` is properly configured:

```yaml
reviews:
  enabled: true
  review_all_files: true
```

### 5. Test CodeRabbit After Disabling Other Bots

1. **Create a Test PR**
   ```bash
   git checkout -b test-coderabbit-only
   # Make a small code change
   echo "# Test" >> README.md
   git add README.md
   git commit -m "Test CodeRabbit review"
   git push origin test-coderabbit-only
   ```

2. **Create PR on GitHub**
   - Go to GitHub and create a PR from `test-coderabbit-only` to `main`
   - Wait 2-5 minutes
   - Check for CodeRabbit review comments

3. **Verify CodeRabbit Review**
   - Look for comments from `@coderabbitai`
   - Check the "Checks" tab for CodeRabbit status
   - Should NOT see "Review skipped" message

## Quick Links

- **Repository Settings**: https://github.com/Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer/settings
- **Installed Apps**: https://github.com/Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer/settings/installations
- **CodeRabbit App**: https://github.com/apps/coderabbitai
- **Macroscope App**: https://github.com/apps/macroscope (if you need to uninstall)

## Troubleshooting

### CodeRabbit Still Skipping?

1. **Check PR Authors**
   - CodeRabbit skips PRs created by bots
   - Ensure PRs are created by human users, not Copilot/Copilot AI

2. **Check for Other Bots**
   - Go to PR → "Checks" tab
   - Look for other bot status checks
   - If you see other AI bots, disable them

3. **Manual Trigger**
   - Comment `@coderabbitai review` in the PR
   - This forces CodeRabbit to review even if it detected other bots

4. **Check CodeRabbit Config**
   ```bash
   cat .coderabbit.yml
   ```
   - Ensure `reviews.enabled: true`
   - Ensure no syntax errors

## After Disabling Other Bots

Once other AI bots are disabled:
- ✅ CodeRabbit will review all PRs automatically
- ✅ No more "Review skipped" messages
- ✅ Full CodeRabbit reviews with suggestions and feedback
- ✅ CodeRabbit will be the only AI code reviewer

---

**Note**: This process requires GitHub repository admin access. If you don't have admin access, ask your repository administrator to disable the other bots.

