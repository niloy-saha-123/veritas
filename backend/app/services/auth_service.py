"""
Authentication service for GitHub OAuth and token management.
"""

from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.database_models import User, UserToken
from datetime import datetime
import requests


class AuthService:
    """Service for handling GitHub OAuth and token management."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, github_id: int, username: str, email: Optional[str] = None, avatar_url: Optional[str] = None) -> User:
        """Get existing user or create new one."""
        user = self.db.query(User).filter(User.github_id == github_id).first()
        if not user:
            user = User(
                github_id=github_id,
                username=username,
                email=email,
                avatar_url=avatar_url
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            # Update user info
            user.username = username
            if email:
                user.email = email
            if avatar_url:
                user.avatar_url = avatar_url
            self.db.commit()
        return user

    def save_user_token(self, user_id: int, token: str, repo_url: str) -> UserToken:
        """Save or update encrypted token for a user."""
        # Check if token already exists for this user and repo
        existing = self.db.query(UserToken).filter(
            UserToken.user_id == user_id,
            UserToken.repo_url == repo_url
        ).first()

        if existing:
            # Update existing token
            existing.encrypted_token = UserToken.encrypt_token(token)
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new token record
            user_token = UserToken(
                user_id=user_id,
                encrypted_token=UserToken.encrypt_token(token),
                repo_url=repo_url
            )
            self.db.add(user_token)
            self.db.commit()
            self.db.refresh(user_token)
            return user_token

    def get_user_token(self, user_id: int, repo_url: str) -> Optional[str]:
        """Get decrypted token for a user and repository."""
        user_token = self.db.query(UserToken).filter(
            UserToken.user_id == user_id,
            UserToken.repo_url == repo_url
        ).first()

        if user_token:
            try:
                return user_token.get_token()
            except Exception as e:
                print(f"Error decrypting token: {e}")
                return None
        return None

    def verify_token_access(self, token: str, repo_url: str) -> bool:
        """Verify that a token has access to the specified repository."""
        try:
            # Parse repo URL to get owner/repo
            import re
            match = re.search(r'github\.com[/:]([\w-]+)/([\w.-]+)', repo_url)
            if not match:
                return False

            owner, repo_name = match.group(1), match.group(2).rstrip('.git')

            # Test token access by trying to get repo info
            # Fine-grained tokens use "Bearer" format, classic tokens use "token" format
            # Try both formats
            headers_bearer = {"Authorization": f"Bearer {token}"}
            headers_token = {"Authorization": f"token {token}"}
            
            # Try Bearer first (for fine-grained tokens)
            response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo_name}",
                headers=headers_bearer,
                timeout=10
            )
            
            # If Bearer fails, try token format (for classic tokens)
            if response.status_code != 200:
                response = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}",
                    headers=headers_token,
                    timeout=10
                )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error verifying token access: {e}")
            return False

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
