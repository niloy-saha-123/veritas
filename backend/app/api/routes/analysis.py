# Analysis API endpoints - POST /analyze for code-doc verification

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional, List
from app.models.schemas import AnalysisRequest, AnalysisResponse, DiscrepancyReport, DiscrepancyType
from app.parsers.parser_factory import parse_code
from app.comparison.scorer import analyze_repository

router = APIRouter()


def _summarize(trust_score: int, issue_count: int) -> str:
    if issue_count == 0:
        return f"Trust score {trust_score}%. No discrepancies found."
    return f"Trust score {trust_score}%. Issues found: {issue_count}."


def _issues_to_discrepancies(issues: List[dict]) -> List[DiscrepancyReport]:
    discrepancies: List[DiscrepancyReport] = []
    for issue in issues:
        # Handle case where issue might not be a dict
        if not isinstance(issue, dict):
            continue
        discrepancies.append(
            DiscrepancyReport(
                type=DiscrepancyType.FUNCTION_SIGNATURE,
                severity=issue.get("severity", "medium"),
                location="unknown",
                description=issue.get("issue", ""),
                code_snippet=issue.get("code_has"),
                doc_snippet=issue.get("docs_say"),
                suggestion=issue.get("suggested_fix"),
            )
        )
    return discrepancies


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_code_and_docs(request: AnalysisRequest):
    """
    Analyze code and documentation for discrepancies.
    
    Args:
        request: Analysis request containing code and documentation URLs/content
        
    Returns:
        AnalysisResponse with detected discrepancies
    """
    try:
        if request.code_url or request.doc_url:
            raise HTTPException(
                status_code=400,
                detail="code_url/doc_url not supported yet. Use code_content and doc_content."
            )

        if not request.code_content or not request.doc_content:
            raise HTTPException(
                status_code=400,
                detail="code_content and doc_content are required."
            )

        code_functions = parse_code("input.py", request.code_content)
        doc_functions = parse_code("docs.md", request.doc_content)

        result = analyze_repository(code_functions, doc_functions)
        discrepancies = _issues_to_discrepancies(result["issues"])

        return AnalysisResponse(
            status="success",
            discrepancies=discrepancies,
            summary=_summarize(result["trust_score"], len(discrepancies)),
            metadata={
                "trust_score": result["trust_score"],
                "total_functions": result["total_functions"],
                "verified": result["verified"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/upload")
async def analyze_uploaded_files(
    code_file: UploadFile = File(...),
    doc_file: Optional[UploadFile] = File(None)
):
    """
    Analyze uploaded code and documentation files.
    
    Args:
        code_file: Source code file
        doc_file: Documentation file (optional)
        
    Returns:
        Analysis results
    """
    try:
        if not doc_file:
            raise HTTPException(status_code=400, detail="doc_file is required")

        code_content = (await code_file.read()).decode("utf-8", errors="ignore")
        doc_content = (await doc_file.read()).decode("utf-8", errors="ignore")

        code_functions = parse_code(code_file.filename or "input.py", code_content)
        doc_functions = parse_code(doc_file.filename or "docs.md", doc_content)

        result = analyze_repository(code_functions, doc_functions)
        discrepancies = _issues_to_discrepancies(result["issues"])

        return AnalysisResponse(
            status="success",
            discrepancies=discrepancies,
            summary=_summarize(result["trust_score"], len(discrepancies)),
            metadata={
                "trust_score": result["trust_score"],
                "total_functions": result["total_functions"],
                "verified": result["verified"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
