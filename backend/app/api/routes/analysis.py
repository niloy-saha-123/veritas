# Analysis API endpoints - POST /analyze for code-doc verification

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.schemas import AnalysisRequest, AnalysisResponse, DiscrepancyReport, DiscrepancyType
from app.parsers.parser_factory import parse_code, get_all_functions
from app.comparison.scorer import analyze_repository

router = APIRouter()


class GitHubAnalysisRequest(BaseModel):
    """Request model for GitHub repository analysis."""
    repo_url: str = Field(..., description="GitHub repository URL (e.g., https://github.com/user/repo)")
    branch: str = Field("main", description="Git branch to analyze (default: main)")
    use_token_company: bool = Field(True, description="Use Token Company for context compression")


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


@router.post("/analyze/github", response_model=AnalysisResponse)
async def analyze_github_repo(request: GitHubAnalysisRequest):
    """
    Intelligent GitHub repository analysis agent.
    
    This agent automatically:
    1. Clones the GitHub repository
    2. Discovers and categorizes all code and documentation files
    3. Maps documentation files to their corresponding code files
    4. Extracts all functions from code and documentation
    5. Uses semantic matching to find documentation for each function
    6. Analyzes discrepancies and provides detailed trust scores
    
    Args:
        request: GitHubAnalysisRequest with repo_url and optional branch
    
    Returns:
        AnalysisResponse with comprehensive analysis results
    
    Example:
        POST /api/v1/analyze/github
        {
            "repo_url": "https://github.com/user/repo",
            "branch": "main",
            "use_token_company": true
        }
    """
    agent = None
    try:
        from app.services.repo_agent import RepoAgent
        
        # Initialize agent
        agent = RepoAgent()
        
        print(f"🤖 Starting intelligent repository analysis for: {request.repo_url}")
        
        # Clone and discover files
        repo_data = agent.clone_and_analyze(
            repo_url=request.repo_url,
            branch=request.branch,
            use_token_company=request.use_token_company
        )
        
        code_files = repo_data['code_files']
        doc_files = repo_data['doc_files']
        mappings = repo_data['mappings']
        
        if not code_files:
            raise HTTPException(
                status_code=400,
                detail=f"No code files found in repository: {request.repo_url}"
            )
        
        if not doc_files:
            raise HTTPException(
                status_code=400,
                detail=f"No documentation files found in repository: {request.repo_url}"
            )
        
        from datetime import datetime
        start_time = datetime.now()
        
        print(f"📊 Parsing {len(code_files)} code files and {len(doc_files)} doc files...")
        print(f"⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Debug: Log file names
        code_file_names = list(code_files.keys())
        print(f"📁 Code files to parse: {code_file_names[:10]}{'...' if len(code_file_names) > 10 else ''}")
        
        # Parse all code files into functions with detailed logging
        all_code_functions = []
        for idx, (filename, content) in enumerate(code_files.items(), 1):
            try:
                parse_start = datetime.now()
                functions = parse_code(filename, content)
                parse_time = (datetime.now() - parse_start).total_seconds()
                if functions:
                    print(f"  [{idx}/{len(code_files)}] {datetime.now().strftime('%H:%M:%S')} ✓ {filename}: {len(functions)} functions ({parse_time:.2f}s)")
                else:
                    print(f"  [{idx}/{len(code_files)}] {datetime.now().strftime('%H:%M:%S')} ⚠ {filename}: 0 functions ({parse_time:.2f}s)")
                all_code_functions.extend(functions)
            except Exception as e:
                print(f"  [{idx}/{len(code_files)}] {datetime.now().strftime('%H:%M:%S')} ❌ {filename}: Error - {e}")
        
        # Parse all doc files into functions with detailed logging
        print(f"\n📄 Parsing {len(doc_files)} documentation files...")
        all_doc_functions = []
        for idx, (filename, content) in enumerate(doc_files.items(), 1):
            try:
                parse_start = datetime.now()
                functions = parse_code(filename, content)  # parse_code handles both code and docs
                parse_time = (datetime.now() - parse_start).total_seconds()
                if functions:
                    print(f"  [{idx}/{len(doc_files)}] {datetime.now().strftime('%H:%M:%S')} ✓ {filename}: {len(functions)} functions ({parse_time:.2f}s)")
                else:
                    print(f"  [{idx}/{len(doc_files)}] {datetime.now().strftime('%H:%M:%S')} ⚠ {filename}: 0 functions ({parse_time:.2f}s)")
                all_doc_functions.extend(functions)
            except Exception as e:
                print(f"  [{idx}/{len(doc_files)}] {datetime.now().strftime('%H:%M:%S')} ❌ {filename}: Error - {e}")
        
        if not all_code_functions:
            # Provide more diagnostic info
            detail_msg = f"No functions extracted from code files. Found {len(code_files)} files: {code_file_names[:5]}..."
            print(f"⚠️  {detail_msg}")
            raise HTTPException(status_code=400, detail=detail_msg)
        
        if not all_doc_functions:
            raise HTTPException(
                status_code=400,
                detail=f"No functions extracted from documentation files. Found {len(doc_files)} files."
            )
        
        print(f"🔧 Found {len(all_code_functions)} code functions and {len(all_doc_functions)} doc functions")
        
        # Analyze entire repository using hybrid engine
        print(f"🧠 Running intelligent analysis with hybrid ML engine...")
        print(f"   Token Company compression: {'enabled' if request.use_token_company else 'disabled'}")
        result = analyze_repository(
            all_code_functions,
            all_doc_functions,
            use_hybrid=True,
            use_token_company=request.use_token_company
        )
        
        discrepancies = _issues_to_discrepancies(result["issues"])
        
        # Build comprehensive metadata
        file_categories = repo_data.get('file_categories', {})
        code_file_list = list(code_files.keys())
        doc_file_list = list(doc_files.keys())
        
        metadata = {
            "trust_score": result["trust_score"],
            "total_functions": result["total_functions"],
            "verified": result["verified"],
            "average_confidence": result.get("average_confidence", 0.0),
            "code_files_analyzed": len(code_files),
            "doc_files_analyzed": len(doc_files),
            "code_file_names": code_file_list[:20],  # Limit to first 20 for response size
            "doc_file_names": doc_file_list[:20],
            "code_functions_count": len(all_code_functions),
            "doc_functions_count": len(all_doc_functions),
            "method_stats": result.get("method_stats", {}),
            "repo_url": request.repo_url,
            "branch": request.branch,
            "file_mappings": {k: v[:5] for k, v in list(mappings.items())[:10]},  # Sample mappings
            "file_categories": {
                "code": len(file_categories.get("code", [])),
                "doc": len(file_categories.get("doc", []))
            }
        }
        
        print(f"✅ Analysis complete! Trust score: {result['trust_score']}%, Issues: {len(discrepancies)}")
        
        # Cleanup temp directory
        agent.cleanup()
        
        return AnalysisResponse(
            status="success",
            discrepancies=discrepancies,
            summary=_summarize(result["trust_score"], len(discrepancies)),
            metadata=metadata,
        )
        
    except HTTPException:
        if agent:
            agent.cleanup()
        raise
    except ImportError as e:
        if agent:
            agent.cleanup()
        raise HTTPException(
            status_code=500,
            detail=f"Missing dependency: {str(e)}. Install with: pip install gitpython"
        )
    except Exception as e:
        if agent:
            agent.cleanup()
        print(f"❌ Error in GitHub repository analysis: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Repository analysis failed: {str(e)}")
