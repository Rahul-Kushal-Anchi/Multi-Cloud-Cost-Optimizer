# How to Check CodeRabbit Reviews

## Quick Checklist ✅

### 1. **On GitHub Pull Request Page**

#### A. Check PR Conversation Tab
- Go to your Pull Request (e.g., PR #2)
- Look for comments from **`@coderabbitai`** or **`@coderabbitai[bot]`**
- CodeRabbit typically posts:
  - A summary comment with review overview
  - Inline comments on specific code lines
  - Suggestions and recommendations

#### B. Check PR Checks Tab
- Click on the **"Checks"** tab in your PR
- Look for **CodeRabbit** status checks
- Green ✅ = Review completed successfully
- Yellow ⚠️ = Review in progress or warnings
- Red ❌ = Review failed or errors

#### C. Check Files Changed Tab
- Click on **"Files changed"** tab
- Look for inline comments from CodeRabbit
- Comments appear as small icons on specific lines
- Click on them to see CodeRabbit's suggestions

### 2. **GitHub Notifications**
- Check your GitHub notifications (bell icon)
- Look for notifications from `coderabbitai[bot]`
- These appear when CodeRabbit:
  - Completes a review
  - Posts comments
  - Responds to your questions

### 3. **CodeRabbit Dashboard** (if available)
- Visit: https://app.coderabbit.ai/
- Sign in with your GitHub account
- View all reviews across your repositories
- See review history and statistics

### 4. **PR Status Indicators**

Look for these indicators in your PR:

```
✅ CodeRabbit Review - Passed
⚠️ CodeRabbit Review - Warning
❌ CodeRabbit Review - Failed
🔄 CodeRabbit Review - In Progress
```

## What CodeRabbit Reviews Include

### Typical Review Components:

1. **Summary Comment**
   - High-level overview of changes
   - Code quality assessment
   - Security concerns (if any)
   - Performance suggestions

2. **Inline Comments**
   - Specific line-by-line feedback
   - Code improvement suggestions
   - Best practices recommendations
   - Bug detection

3. **Review Categories**
   - 🐛 **Bugs**: Potential issues found
   - 💡 **Suggestions**: Code improvements
   - ⚠️ **Warnings**: Things to be aware of
   - ✅ **Approvals**: Code looks good

## How to Verify CodeRabbit is Working

### Test Steps:

1. **Create a Test PR**
   ```bash
   git checkout -b test-coderabbit-check
   # Make some code changes
   git add .
   git commit -m "Test CodeRabbit review"
   git push origin test-coderabbit-check
   ```
   Then create a PR on GitHub

2. **Wait 2-5 minutes** after PR creation
   - CodeRabbit usually reviews within minutes

3. **Check for CodeRabbit Activity**
   - Look for bot comments
   - Check the Checks tab
   - Review inline comments

### If CodeRabbit Doesn't Appear:

1. **Check GitHub App Installation**
   - Go to: https://github.com/settings/installations
   - Verify CodeRabbit app is installed
   - Ensure it has access to your repository

2. **Check Configuration File**
   - Verify `.coderabbit.yml` exists in repo root
   - Check for syntax errors
   - Ensure `reviews.enabled: true`

3. **Check Repository Settings**
   - Go to: Repository → Settings → Integrations
   - Verify CodeRabbit has necessary permissions

## Example: What a CodeRabbit Review Looks Like

```
@coderabbitai commented:

📋 Summary
This PR introduces changes to the API configuration...

✅ Strengths
- Clean code structure
- Good error handling

⚠️ Suggestions
- Consider adding type hints
- Add unit tests for new functions

💡 Recommendations
- Line 45: Use f-strings instead of .format()
- Line 78: Add input validation

Estimated Review Time: ~10 minutes
```

## Troubleshooting

### CodeRabbit Not Reviewing?

1. **Check PR Status**
   - Is the PR in draft mode? (CodeRabbit may skip drafts)
   - Is the PR too large? (may take longer)

2. **Check Configuration**
   ```bash
   cat .coderabbit.yml
   ```
   - Verify YAML syntax is correct
   - Check that reviews are enabled

3. **Check GitHub App Status**
   - Repository → Settings → Apps
   - Find CodeRabbit
   - Verify it's active

4. **Manual Trigger** (if supported)
   - Comment `@coderabbitai review` in PR
   - Or use: `@coderabbitai help` for commands

## Useful CodeRabbit Commands

Comment these in your PR to interact with CodeRabbit:

- `@coderabbitai help` - Show available commands
- `@coderabbitai review` - Request a review
- `@coderabbitai explain` - Explain specific code
- `@coderabbitai summarize` - Summarize changes

## Quick Reference

| Location | What to Look For |
|----------|------------------|
| PR Conversation | Comments from `@coderabbitai` |
| Checks Tab | CodeRabbit status check |
| Files Changed | Inline comments on code |
| Notifications | CodeRabbit activity alerts |
| Dashboard | Review history (if available) |

---

**Note**: CodeRabbit reviews are typically automatic on PR creation, but may take a few minutes to complete.

