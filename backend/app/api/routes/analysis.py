# Analysis API endpoints - POST /analyze for code-doc verification

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional, List
from app.models.schemas import AnalysisRequest, AnalysisResponse, DiscrepancyReport, DiscrepancyType
from app.parsers.parser_factory import parse_code, get_all_functions
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


@router.post("/analyze/batch", response_model=AnalysisResponse)
async def analyze_batch_files(
    code_files: List[UploadFile] = File(...),
    doc_files: Optional[List[UploadFile]] = File(None)
):
    """
    Analyze multiple code and documentation files at once (whole repository support).
    
    This endpoint allows analyzing entire codebases by accepting multiple files.
    All code files are analyzed together against all documentation files.
    
    Args:
        code_files: List of source code files (.py, .js, .java, etc.)
        doc_files: List of documentation files (.md, .json, etc.)
    
    Returns:
        AnalysisResponse with aggregated results across all files
    
    Example:
        curl -X POST "http://localhost:8000/api/v1/analyze/batch" \\
            -F "code_files=@file1.py" \\
            -F "code_files=@file2.py" \\
            -F "doc_files=@docs.md" \\
            -F "doc_files=@api.json"
    """
    try:
        if not code_files or len(code_files) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one code_file is required"
            )
        
        if not doc_files or len(doc_files) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one doc_file is required"
            )
        
        # Collect all code files content
        code_files_dict = {}
        code_file_names = []
        for file in code_files:
            try:
                content = (await file.read()).decode("utf-8", errors="ignore")
                filename = file.filename or "unknown"
                code_files_dict[filename] = content
                code_file_names.append(filename)
            except Exception as e:
                print(f"⚠️  Error reading code file {file.filename}: {e}")
                continue
        
        if not code_files_dict:
            raise HTTPException(
                status_code=400,
                detail="No valid code files could be read"
            )
        
        # Collect all doc files content
        doc_files_dict = {}
        doc_file_names = []
        for file in doc_files:
            try:
                content = (await file.read()).decode("utf-8", errors="ignore")
                filename = file.filename or "unknown"
                doc_files_dict[filename] = content
                doc_file_names.append(filename)
            except Exception as e:
                print(f"⚠️  Error reading doc file {file.filename}: {e}")
                continue
        
        if not doc_files_dict:
            raise HTTPException(
                status_code=400,
                detail="No valid documentation files could be read"
            )
        
        # Parse all code files into functions
        all_code_functions = get_all_functions(code_files_dict)
        
        # Parse all doc files into functions
        all_doc_functions = get_all_functions(doc_files_dict)
        
        if not all_code_functions:
            raise HTTPException(
                status_code=400,
                detail=f"No functions found in code files: {code_file_names}"
            )
        
        if not all_doc_functions:
            raise HTTPException(
                status_code=400,
                detail=f"No functions found in documentation files: {doc_file_names}"
            )
        
        # Analyze entire repository (all functions from all files)
        result = analyze_repository(all_code_functions, all_doc_functions, use_hybrid=True)
        discrepancies = _issues_to_discrepancies(result["issues"])
        
        # Enhance metadata with file statistics
        metadata = {
            "trust_score": result["trust_score"],
            "total_functions": result["total_functions"],
            "verified": result["verified"],
            "average_confidence": result.get("average_confidence", 0.0),
            "code_files_analyzed": len(code_files_dict),
            "doc_files_analyzed": len(doc_files_dict),
            "code_file_names": code_file_names,
            "doc_file_names": doc_file_names,
            "code_functions_count": len(all_code_functions),
            "doc_functions_count": len(all_doc_functions),
            "method_stats": result.get("method_stats", {}),
        }
        
        return AnalysisResponse(
            status="success",
            discrepancies=discrepancies,
            summary=_summarize(result["trust_score"], len(discrepancies)),
            metadata=metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in batch analysis: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
