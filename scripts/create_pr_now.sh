#!/bin/bash

# Script to create PR automatically using GitHub API
# Usage: GITHUB_TOKEN=your_token ./create_pr_now.sh

set -e

REPO_OWNER="Rahul-Kushal-Anchi"
REPO_NAME="Multi-Cloud-Cost-Optimizer"
HEAD_BRANCH="test-coderabbit-only-review"
BASE_BRANCH="main"
TITLE="Test CodeRabbit review (no other bots)"
BODY="This PR tests CodeRabbit review functionality without other AI bots.

**Changes:**
- Added a comment for better code documentation in api/main.py

**Purpose:**
- Verify CodeRabbit reviews PRs when other bots are disabled
- Test CodeRabbit's review capabilities"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable is required"
    echo ""
    echo "To get a token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Select 'repo' scope"
    echo "4. Copy the token"
    echo ""
    echo "Then run:"
    echo "  export GITHUB_TOKEN=your_token_here"
    echo "  ./create_pr_now.sh"
    exit 1
fi

echo "🚀 Creating pull request..."
echo "   Title: $TITLE"
echo "   From: $HEAD_BRANCH -> To: $BASE_BRANCH"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/pulls" \
  -d "{
    \"title\": \"$TITLE\",
    \"head\": \"$HEAD_BRANCH\",
    \"base\": \"$BASE_BRANCH\",
    \"body\": $(echo "$BODY" | jq -Rs .)
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY_RESPONSE=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 201 ]; then
    PR_URL=$(echo "$BODY_RESPONSE" | jq -r '.html_url')
    PR_NUMBER=$(echo "$BODY_RESPONSE" | jq -r '.number')
    
    echo "✅ Pull request created successfully!"
    echo ""
    echo "   PR #$PR_NUMBER: $PR_URL"
    echo ""
    echo "⏱️  CodeRabbit will review this PR within 2-5 minutes."
    echo "   Check: $PR_URL"
else
    echo "❌ Error creating pull request (HTTP $HTTP_CODE)"
    echo "$BODY_RESPONSE" | jq '.' 2>/dev/null || echo "$BODY_RESPONSE"
    exit 1
fi

