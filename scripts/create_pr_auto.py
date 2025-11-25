#!/usr/bin/env python3
"""
Automatically create a pull request using GitHub API
"""

import os
import sys
import json
import urllib.request
import urllib.parse


def create_pr(token, repo_owner, repo_name, head_branch, base_branch, title, body):
    """Create a pull request using GitHub API"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"

    data = {"title": title, "head": head_branch, "base": base_branch, "body": body}

    json_data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=json_data)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"Error creating PR: {e.code}")
        print(f"Response: {error_body}")
        sys.exit(1)


def main():
    repo_owner = "Rahul-Kushal-Anchi"
    repo_name = "Multi-Cloud-Cost-Optimizer"
    head_branch = "test-coderabbit-only-review"
    base_branch = "main"
    title = "Test CodeRabbit review (no other bots)"
    body = """This PR tests CodeRabbit review functionality without other AI bots.

**Changes:**
- Added a comment for better code documentation in api/main.py

**Purpose:**
- Verify CodeRabbit reviews PRs when other bots are disabled
- Test CodeRabbit's review capabilities"""

    # Try to get token from environment or prompt
    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        print("GitHub token not found in environment.")
        print("Please set GITHUB_TOKEN environment variable or enter it below:")
        token = input("GitHub Token: ").strip()

        if not token:
            print("Error: GitHub token is required")
            print("\nTo get a token:")
            print("1. Go to: https://github.com/settings/tokens")
            print("2. Click 'Generate new token (classic)'")
            print("3. Select 'repo' scope")
            print("4. Copy the token")
            print("\nThen run: export GITHUB_TOKEN=your_token_here")
            sys.exit(1)

    print(f"Creating pull request: {title}")
    print(f"From: {head_branch} -> To: {base_branch}")

    result = create_pr(
        token, repo_owner, repo_name, head_branch, base_branch, title, body
    )

    print("\n✅ Pull request created successfully!")
    print(f"PR Number: #{result['number']}")
    print(f"URL: {result['html_url']}")
    print(f"\nCodeRabbit should review this PR within 2-5 minutes.")
    print(f"Check: {result['html_url']}")


if __name__ == "__main__":
    main()
