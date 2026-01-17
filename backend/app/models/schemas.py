# Pydantic data models - defines request/response schemas for API validation

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class DiscrepancyType(str, Enum):
    """Types of discrepancies that can be detected."""
    FUNCTION_SIGNATURE = "function_signature"
    PARAMETER_TYPE = "parameter_type"
    RETURN_TYPE = "return_type"
    MISSING_DOCUMENTATION = "missing_documentation"
    OUTDATED_EXAMPLE = "outdated_example"
    DEPRECATED_USAGE = "deprecated_usage"


class DiscrepancyReport(BaseModel):
    """Individual discrepancy report."""
    type: DiscrepancyType
    severity: str = Field(..., description="low, medium, high, critical")
    location: str = Field(..., description="File path and line number")
    description: str
    code_snippet: Optional[str] = None
    doc_snippet: Optional[str] = None
    suggestion: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request model for code/documentation analysis."""
    code_url: Optional[str] = Field(None, description="URL to code repository")
    doc_url: Optional[str] = Field(None, description="URL to documentation")
    code_content: Optional[str] = Field(None, description="Raw code content")
    doc_content: Optional[str] = Field(None, description="Raw documentation content")
    language: str = Field("python", description="Programming language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code_url": "https://github.com/user/repo",
                "doc_url": "https://docs.example.com",
                "language": "python"
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    status: str
    discrepancies: List[DiscrepancyReport]
    summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
