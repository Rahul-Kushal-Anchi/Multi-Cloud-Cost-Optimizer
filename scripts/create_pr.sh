#!/bin/bash

# Script to create a pull request for CodeRabbit test
# Usage: GITHUB_TOKEN=your_token ./create_pr.sh

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Usage: GITHUB_TOKEN=your_token ./create_pr.sh"
    exit 1
fi

curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer/pulls \
  -d '{
    "title": "Test CodeRabbit review",
    "head": "test-coderabbit-review",
    "base": "main",
    "body": "This PR tests CodeRabbit automated code review functionality.\n\n**Changes:**\n- Fixed duplicate sys import in api/main.py\n- Added CodeRabbit configuration (.coderabbit.yml)\n\n**Purpose:**\n- Verify CodeRabbit is working correctly\n- Test automated code review on Python code"
  }'

echo ""
echo "PR created successfully!"

