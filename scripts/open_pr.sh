#!/bin/bash
# Open PR creation page with pre-filled data

PR_URL="https://github.com/Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer/compare/main...test-coderabbit-only-review?expand=1&title=Test%20CodeRabbit%20review%20(no%20other%20bots)&body=This%20PR%20tests%20CodeRabbit%20review%20functionality%20without%20other%20AI%20bots.%0A%0A**Changes:**%0A-%20Added%20a%20comment%20for%20better%20code%20documentation%20in%20api/main.py%0A%0A**Purpose:**%0A-%20Verify%20CodeRabbit%20reviews%20PRs%20when%20other%20bots%20are%20disabled%0A-%20Test%20CodeRabbit%27s%20review%20capabilities"

echo "Opening PR creation page..."
echo "URL: $PR_URL"
echo ""
echo "Once the page opens:"
echo "1. Sign in if needed"
echo "2. Click the green 'Create pull request' button"
echo "3. Done! CodeRabbit will review automatically"

# Try to open in default browser
if command -v open >/dev/null 2>&1; then
    open "$PR_URL"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$PR_URL"
else
    echo "Please open this URL in your browser:"
    echo "$PR_URL"
fi
