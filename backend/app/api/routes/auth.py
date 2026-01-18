"""
Authentication routes for GitHub OAuth and token management.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
import requests
import secrets

from app.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.models.database_models import User, UserToken

router = APIRouter()

# Store OAuth states temporarily (in production, use Redis)
oauth_states = {}


class TokenSaveRequest(BaseModel):
    """Request to save a GitHub token."""
    token: str = Field(..., description="GitHub fine-grained token")
    repo_url: str = Field(..., description="Repository URL the token has access to")
    user_id: int = Field(..., description="User ID")


class TokenSaveResponse(BaseModel):
    """Response after saving token."""
    success: bool
    message: str


class UserInfo(BaseModel):
    """User information."""
    id: int
    github_id: int
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("/auth/github")
async def github_oauth_redirect(request: Request):
    """Redirect to GitHub OAuth."""
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth not configured. Set GITHUB_CLIENT_ID in .env"
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True
    
    # GitHub OAuth URL - redirect back to backend callback endpoint
    # Construct callback URL
    base_url = str(request.base_url).rstrip('/')
    redirect_uri = f"{base_url}/api/v1/auth/github/callback"
    github_oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=read:user user:email"
        f"&state={state}"
    )
    
    return RedirectResponse(url=github_oauth_url)


@router.get("/auth/github/callback")
async def github_oauth_callback(
    code: str,
    state: str
):
    """Handle GitHub OAuth callback."""
    # Verify state
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    del oauth_states[state]
    
    if not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth not configured. Set GITHUB_CLIENT_SECRET in .env"
        )
    
    # Exchange code for access token
    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
        },
        timeout=10
    )
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")
    
    # Get user info from GitHub
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {access_token}"},
        timeout=10
    )
    
    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info")
    
    user_data = user_response.json()
    
    # Get user email
    email = user_data.get("email")
    if not email:
        emails_response = requests.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"token {access_token}"},
            timeout=10
        )
        if emails_response.status_code == 200:
            emails = emails_response.json()
            email = next((e["email"] for e in emails if e.get("primary")), None)
    
    # Create or update user in database
    db = next(get_db())
    auth_service = AuthService(db)
    user = auth_service.get_or_create_user(
        github_id=user_data["id"],
        username=user_data["login"],
        email=email,
        avatar_url=user_data.get("avatar_url")
    )
    
    # Commit any pending changes and refresh to get the user ID
    db.commit()
    db.refresh(user)
    print(f"✅ User created/updated: ID={user.id}, GitHub ID={user.github_id}, Username={user.username}")
    
    # Redirect to frontend with user info
    # Use Vite dev server port (5173) or first allowed origin with 5173
    frontend_url = "http://localhost:5173"  # Default to Vite dev server
    if settings.ALLOWED_ORIGINS:
        # Check if 5173 is in the list, otherwise use first
        vite_url = next((url for url in settings.ALLOWED_ORIGINS if "5173" in url), None)
        if vite_url:
            frontend_url = vite_url
        else:
            frontend_url = settings.ALLOWED_ORIGINS[0]
    redirect_url = f"{frontend_url}/?user_id={user.id}&username={user.username}"
    return RedirectResponse(url=redirect_url)


@router.post("/auth/save-token", response_model=TokenSaveResponse)
async def save_token(
    request: TokenSaveRequest,
    db: Session = Depends(get_db)
):
    """Save encrypted GitHub token for a user."""
    try:
        auth_service = AuthService(db)
        
        # Verify user exists
        print(f"🔍 Looking for user with ID: {request.user_id}")
        user = auth_service.get_user_by_id(request.user_id)
        if not user:
            # Log all users for debugging
            all_users = db.query(User).all()
            print(f"⚠️  User {request.user_id} not found. Total users in DB: {len(all_users)}")
            if all_users:
                print(f"   Existing user IDs: {[u.id for u in all_users]}")
            raise HTTPException(status_code=404, detail=f"User not found with ID: {request.user_id}")
        print(f"✅ Found user: {user.id} - {user.username}")
        
        # Verify token has access to the repository
        try:
            has_access = auth_service.verify_token_access(request.token, request.repo_url)
            if not has_access:
                raise HTTPException(
                    status_code=400,
                    detail="Token does not have access to the specified repository. Please check that the token has 'Issues: Read and write' permission for this repository."
                )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error verifying token access: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to verify token access: {str(e)}"
            )
        
        # Save encrypted token
        auth_service.save_user_token(request.user_id, request.token, request.repo_url)
        
        return TokenSaveResponse(
            success=True,
            message="Token saved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving token: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save token: {str(e)}")


@router.get("/auth/user/{user_id}", response_model=UserInfo)
async def get_user_info(user_id: int, db: Session = Depends(get_db)):
    """Get user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserInfo(
        id=user.id,
        github_id=user.github_id,
        username=user.username,
        email=user.email,
        avatar_url=user.avatar_url
    )


@router.get("/auth/user/{user_id}/token/{repo_url}")
async def get_user_token(user_id: int, repo_url: str, db: Session = Depends(get_db)):
    """Get decrypted token for a user and repository."""
    auth_service = AuthService(db)
    token = auth_service.get_user_token(user_id, repo_url)
    
    if not token:
        raise HTTPException(
            status_code=404,
            detail="No token found for this user and repository"
        )
    
    return {"token": token}
