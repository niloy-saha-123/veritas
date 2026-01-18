"""
PR Analysis API endpoints

Premium feature: Analyze GitHub Pull Requests for documentation issues.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.pr_analyzer import PRAnalyzer, PRAnalysisResult
from app.services.auth_service import AuthService
from app.models.schemas import DiscrepancyReport

router = APIRouter()


class PRAnalysisRequest(BaseModel):
    """Request model for PR analysis."""
    repo_url: str = Field(..., description="GitHub repository URL")
    pr_number: int = Field(..., description="Pull request number")
    github_token: Optional[str] = Field(None, description="GitHub token (optional, can use user's stored token)")
    user_id: Optional[int] = Field(None, description="User ID to use stored token")
    post_comment: bool = Field(False, description="Whether to post results as PR comment")


class PRAnalysisResponse(BaseModel):
    """Response model for PR analysis."""
    success: bool
    pr_number: int
    repo_url: str
    total_changes: int
    files_analyzed: int
    new_functions: List[dict]
    modified_functions: List[dict]
    missing_docs: List[dict]
    outdated_docs: List[dict]
    discrepancies: List[dict]
    trust_score: int
    summary: str
    comment_url: Optional[str] = None
    error: Optional[str] = None


@router.post("/analyze/pr", response_model=PRAnalysisResponse)
async def analyze_pull_request(
    request: PRAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a GitHub Pull Request for documentation issues.
    
    Premium feature: Analyzes PR changes and detects:
    - New functions without documentation
    - Modified functions with outdated docs
    - Documentation discrepancies
    
    Args:
        request: PR analysis request
        db: Database session
        
    Returns:
        PRAnalysisResponse with analysis results
    """
    try:
        # Get GitHub token
        github_token = request.github_token
        
        if not github_token and request.user_id:
            # Try to get token from user's stored tokens
            auth_service = AuthService(db)
            user_tokens = auth_service.get_user_tokens(request.user_id)
            
            # Find token for this repository
            matching_token = next(
                (token for token in user_tokens if token.repo_url == request.repo_url),
                None
            )
            
            if matching_token:
                github_token = matching_token.decrypt_token()
        
        if not github_token:
            # Fallback to environment variable
            from app.core.config import settings
            github_token = settings.GITHUB_TOKEN
        
        if not github_token:
            raise HTTPException(
                status_code=400,
                detail="GitHub token is required. Provide github_token in request, user_id with stored token, or set GITHUB_TOKEN in environment."
            )
        
        # Analyze PR
        analyzer = PRAnalyzer(github_token)
        result = analyzer.analyze_pr(request.repo_url, request.pr_number)
        
        # Post comment if requested
        comment_url = None
        if request.post_comment:
            try:
                comment_url = analyzer.post_pr_comment(request.repo_url, request.pr_number, result)
            except Exception as e:
                print(f"Failed to post PR comment: {e}")
                # Don't fail the whole request if comment posting fails
        
        # Convert discrepancies to dicts for response
        discrepancies_dict = []
        for disc in result.discrepancies:
            discrepancies_dict.append({
                "type": disc.type.value if hasattr(disc.type, 'value') else str(disc.type),
                "severity": disc.severity,
                "location": disc.location,
                "description": disc.description,
                "code_snippet": disc.code_snippet,
                "doc_snippet": disc.doc_snippet,
                "suggestion": disc.suggestion,
            })
        
        return PRAnalysisResponse(
            success=True,
            pr_number=result.pr_number,
            repo_url=result.repo_url,
            total_changes=result.total_changes,
            files_analyzed=result.files_analyzed,
            new_functions=result.new_functions,
            modified_functions=result.modified_functions,
            missing_docs=result.missing_docs,
            outdated_docs=result.outdated_docs,
            discrepancies=discrepancies_dict,
            trust_score=result.trust_score,
            summary=result.summary,
            comment_url=comment_url
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"PR analysis not available: {str(e)}")
    except Exception as e:
        print(f"Error analyzing PR: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze PR: {str(e)}"
        )


@router.post("/analyze/pr/comment")
async def post_pr_analysis_comment(
    repo_url: str,
    pr_number: int,
    github_token: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Post PR analysis results as a comment on the PR.
    
    This endpoint first analyzes the PR, then posts the results as a comment.
    
    Args:
        repo_url: GitHub repository URL
        pr_number: Pull request number
        github_token: GitHub token (optional)
        user_id: User ID to use stored token (optional)
        db: Database session
        
    Returns:
        Comment URL and analysis summary
    """
    try:
        # Get GitHub token (same logic as analyze_pull_request)
        if not github_token and user_id:
            auth_service = AuthService(db)
            user_tokens = auth_service.get_user_tokens(user_id)
            matching_token = next(
                (token for token in user_tokens if token.repo_url == repo_url),
                None
            )
            if matching_token:
                github_token = matching_token.decrypt_token()
        
        if not github_token:
            from app.core.config import settings
            github_token = settings.GITHUB_TOKEN
        
        if not github_token:
            raise HTTPException(
                status_code=400,
                detail="GitHub token is required"
            )
        
        # Analyze and post comment
        analyzer = PRAnalyzer(github_token)
        result = analyzer.analyze_pr(repo_url, pr_number)
        comment_url = analyzer.post_pr_comment(repo_url, pr_number, result)
        
        return {
            "success": True,
            "comment_url": comment_url,
            "summary": result.summary,
            "trust_score": result.trust_score
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to post PR comment: {str(e)}"
        )
