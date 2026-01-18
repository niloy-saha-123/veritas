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


# ============================================================================
# PARSER MODELS - Used by Person A's parsers to return function signatures
# ============================================================================

class Parameter(BaseModel):
    """Single function parameter with type info."""
    name: str
    type: Optional[str] = None  # Type annotation if available
    default: Optional[str] = None  # Default value if any
    
    def __repr__(self):
        if self.type and self.default:
            return f"{self.name}: {self.type} = {self.default}"
        elif self.type:
            return f"{self.name}: {self.type}"
        elif self.default:
            return f"{self.name}={self.default}"
        return self.name


class FunctionSignature(BaseModel):
    """Extracted function signature from code."""
    name: str  # Function name
    params: List[Parameter] = []  # List of parameters
    return_type: Optional[str] = None  # Return type annotation
    docstring: Optional[str] = None  # Docstring content
    line_number: int = 0  # Line where function starts
    is_async: bool = False  # async functions
    is_method: bool = False  # True if inside a class
    class_name: Optional[str] = None  # Parent class name if method
    filename: Optional[str] = None  # Source file
    
    def __repr__(self):
        params_str = ", ".join(str(p) for p in self.params)
        ret = f" -> {self.return_type}" if self.return_type else ""
        prefix = "async " if self.is_async else ""
        return f"{prefix}def {self.name}({params_str}){ret}"


class CreateIssueRequest(BaseModel):
    """Request model for creating an Issue with documentation discrepancies."""
    repo_url: str = Field(..., description="GitHub repository URL")
    discrepancies: List[DiscrepancyReport] = Field(..., description="List of discrepancies found")
    metadata: Dict[str, Any] = Field(..., description="Analysis metadata")
    issue_title: Optional[str] = Field(None, description="Custom Issue title")
    issue_body: Optional[str] = Field(None, description="Custom Issue body")
    user_id: Optional[int] = Field(None, description="User ID for retrieving stored token")


class CreateIssueResponse(BaseModel):
    """Response model for Issue creation."""
    success: bool
    issue_url: Optional[str] = None
    error: Optional[str] = None

