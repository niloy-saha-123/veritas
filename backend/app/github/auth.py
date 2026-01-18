# backend/app/github/auth.py
"""
GitHub App authentication using JWT
"""

import jwt
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")

def generate_jwt() -> str:
    """Generate JWT for GitHub App authentication."""
    
    now = int(time.time())
    payload = {
        "iat": now,           # Issued at
        "exp": now + 600,     # Expires in 10 minutes
        "iss": GITHUB_APP_ID  # Issuer (your app ID)
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