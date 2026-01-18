# backend/app/github/auth.py
"""
GitHub App authentication - JWT, tokens, PR creation, issue creation
"""

import jwt
import time
import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY", "").replace("\\n", "\n")


def generate_jwt() -> str:
    """Generate JWT for GitHub App authentication."""
    
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 600,
        "iss": GITHUB_APP_ID
    }
    
    return jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")


def get_installation_token(installation_id: int) -> str:
    """Get installation access token for specific installation."""
    
    jwt_token = generate_jwt()
    
    response = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json"
        }
    )
    
    if response.status_code != 201:
        raise Exception(f"Failed to get installation token: {response.text}")
    
    return response.json()["token"]


def post_pr_comment(repo: str, pr_number: int, token: str, comment: str):
    """Post a comment on a GitHub PR."""
    
    response = requests.post(
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={"body": comment}
    )
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to post comment: {response.text}")
    
    return response.json()


def create_fix_pr(
    repo: str,
    token: str,
    base_branch: str,
    title: str,
    body: str,
    files: dict
) -> int:
    """
    Create a PR with documentation fixes.
    
    Args:
        repo: Repository name (owner/repo)
        token: Installation access token
        base_branch: Branch to create PR against
        title: PR title
        body: PR description
        files: Dict of {filename: content}
    
    Returns:
        PR number
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    
    # Create branch name
    branch_name = f"veritas/docs-fix-{int(time.time())}"
    
    # Get base branch SHA
    response = requests.get(
        f"https://api.github.com/repos/{repo}/git/refs/heads/{base_branch}",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get base branch: {response.text}")
    
    base_sha = response.json()["object"]["sha"]
    
    # Create new branch
    response = requests.post(
        f"https://api.github.com/repos/{repo}/git/refs",
        headers=headers,
        json={
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
    )
    
    if response.status_code != 201:
        raise Exception(f"Failed to create branch: {response.text}")
    
    # Add/update files in the new branch
    for filename, content in files.items():
        # Check if file exists
        file_response = requests.get(
            f"https://api.github.com/repos/{repo}/contents/{filename}",
            headers=headers,
            params={"ref": branch_name}
        )
        
        file_sha = None
        if file_response.status_code == 200:
            file_sha = file_response.json().get("sha")
        
        # Create/update file
        content_b64 = base64.b64encode(content.encode()).decode()
        
        update_data = {
            "message": f"docs: Add/update {filename}",
            "content": content_b64,
            "branch": branch_name
        }
        
        if file_sha:
            update_data["sha"] = file_sha
        
        response = requests.put(
            f"https://api.github.com/repos/{repo}/contents/{filename}",
            headers=headers,
            json=update_data
        )
        
        if response.status_code not in [200, 201]:
            print(f"Warning: Failed to update {filename}: {response.text}")
    
    # Create PR
    response = requests.post(
        f"https://api.github.com/repos/{repo}/pulls",
        headers=headers,
        json={
            "title": title,
            "body": body,
            "head": branch_name,
            "base": base_branch
        }
    )
    
    if response.status_code != 201:
        raise Exception(f"Failed to create PR: {response.text}")
    
    return response.json()["number"]


def create_issue(
    repo: str,
    token: str,
    title: str,
    body: str,
    labels: list = None
) -> int:
    """
    Create a GitHub issue.
    
    Args:
        repo: Repository name (owner/repo)
        token: Installation access token
        title: Issue title
        body: Issue description
        labels: List of label names
    
    Returns:
        Issue number
    """
    
    response = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "title": title,
            "body": body,
            "labels": labels or []
        }
    )
    
    if response.status_code != 201:
        raise Exception(f"Failed to create issue: {response.text}")
    
    return response.json()["number"]