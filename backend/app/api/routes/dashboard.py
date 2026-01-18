"""
Dashboard routes for user profile, repositories, and analysis history.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.database_models import User, UserToken, AnalysisHistory
from app.services.auth_service import AuthService
import json

router = APIRouter()


class RepositoryInfo(BaseModel):
    """Repository information."""
    id: int
    repo_url: str
    created_at: datetime


class AnalysisHistoryItem(BaseModel):
    """Analysis history item."""
    id: int
    repo_url: str
    trust_score: int
    total_functions: int
    verified_count: int
    discrepancies_count: int
    created_at: datetime
    metadata: Optional[dict] = None  # Full analysis data


class DashboardResponse(BaseModel):
    """Dashboard data response."""
    user_id: int
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    repositories: List[RepositoryInfo]
    analysis_history: List[AnalysisHistoryItem]


@router.get("/dashboard/{user_id}", response_model=DashboardResponse)
async def get_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get dashboard data for a user."""
    auth_service = AuthService(db)
    
    # Get user info
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's repositories (from stored tokens)
    repo_tokens = db.query(UserToken).filter(UserToken.user_id == user_id).all()
    repositories = [
        RepositoryInfo(
            id=token.id,
            repo_url=token.repo_url,
            created_at=token.created_at
        )
        for token in repo_tokens
    ]
    
    # Get analysis history (last 3 analyses only)
    history_records = db.query(AnalysisHistory).filter(
        AnalysisHistory.user_id == user_id
    ).order_by(AnalysisHistory.created_at.desc()).limit(3).all()
    
    analysis_history = [
        AnalysisHistoryItem(
            id=record.id,
            repo_url=record.repo_url,
            trust_score=record.trust_score,
            total_functions=record.total_functions,
            verified_count=record.verified_count,
            discrepancies_count=record.discrepancies_count,
            created_at=record.created_at,
            metadata=json.loads(record.analysis_data) if record.analysis_data else None
        )
        for record in history_records
    ]
    
    return DashboardResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        avatar_url=user.avatar_url,
        repositories=repositories,
        analysis_history=analysis_history
    )


@router.post("/dashboard/analysis/history")
async def save_analysis_history(
    user_id: int,
    repo_url: str,
    trust_score: int,
    total_functions: int,
    verified_count: int,
    discrepancies_count: int,
    metadata: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Save analysis history for a user."""
    history = AnalysisHistory(
        user_id=user_id,
        repo_url=repo_url,
        trust_score=trust_score,
        total_functions=total_functions,
        verified_count=verified_count,
        discrepancies_count=discrepancies_count,
        metadata=json.dumps(metadata) if metadata else None
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    
    return {"success": True, "id": history.id}


@router.delete("/dashboard/analysis/history/{history_id}")
async def delete_analysis_history(
    history_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete an analysis history entry."""
    history = db.query(AnalysisHistory).filter(
        AnalysisHistory.id == history_id,
        AnalysisHistory.user_id == user_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Analysis history not found")
    
    db.delete(history)
    db.commit()
    
    return {"success": True, "message": "Analysis history deleted successfully"}


@router.delete("/dashboard/repository/{repo_id}")
async def delete_repository(
    repo_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a connected repository."""
    repo_token = db.query(UserToken).filter(
        UserToken.id == repo_id,
        UserToken.user_id == user_id
    ).first()
    
    if not repo_token:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    db.delete(repo_token)
    db.commit()
    
    return {"success": True, "message": "Repository deleted successfully"}
