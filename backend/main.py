from fastapi import FastAPI, BackgroundTasks, Request  # ← Add Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uuid
from app.github.webhook_handler import handle_webhook
from enum import Enum

app = FastAPI(title="Veritas.dev API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"

class AnalyzeRequest(BaseModel):
    github_url: str

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus

jobs: Dict[str, Dict[str, Any]] = {}

@app.get("/")
def root():
    return {
        "service": "Veritas.dev API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "POST /analyze",
            "results": "GET /results/{job_id}",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok", "jobs": len(jobs)}

@app.post("/analyze", response_model=JobResponse)
async def analyze_repo(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    if not request.github_url.startswith("https://github.com/"):
        return {"error": "Invalid GitHub URL"}, 400
    
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "status": JobStatus.PENDING,
        "github_url": request.github_url,
        "result": None,
        "progress": None
    }
    
    # Enable background processing
    background_tasks.add_task(process_analysis, job_id, request.github_url)
    
    return JobResponse(job_id=job_id, status=JobStatus.PENDING)

@app.get("/results/{job_id}")
async def get_results(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}, 404
    return jobs[job_id]

@app.post("/github/webhook")
async def github_webhook(request: Request):
    """GitHub App webhook endpoint."""
    from app.github.webhook_handler import handle_webhook
    return await handle_webhook(request)

# ============= BACKGROUND PROCESSING =============

async def process_analysis(job_id: str, github_url: str):
    """Background task to analyze repository."""
    jobs[job_id]["status"] = JobStatus.PROCESSING
    
    try:
        # Import everything
        from app.utils.git_utils import clone_repo, discover_files, cleanup_repo
        from app.parsers.parser_factory import parse_code
        from app.parsers.markdown_parser import parse_markdown
        from app.comparison.hybrid_engine import HybridComparator
        
        # Step 1: Clone repo
        jobs[job_id]["progress"] = "Cloning repository..."
        repo_path = clone_repo(github_url)
        files = discover_files(repo_path)
        
        jobs[job_id]["progress"] = f"Found {len(files['code'])} code files, {len(files['docs'])} doc files"
        
        # Step 2: Parse code files (multi-language)
        jobs[job_id]["progress"] = "Parsing code files..."
        code_functions = []
        
        for code_file in files['code']:
            try:
                with open(code_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    functions = parse_code(code_file, content)
                    code_functions.extend(functions)
            except Exception as e:
                print(f"Error parsing {code_file}: {e}")
        
        jobs[job_id]["progress"] = f"Parsed {len(code_functions)} functions from code"
        
        # Step 3: Parse doc files
        jobs[job_id]["progress"] = "Parsing documentation..."
        doc_functions = []
        
        for doc_file in files['docs']:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    docs = parse_markdown(content)
                    doc_functions.extend(docs)
            except Exception as e:
                print(f"Error parsing {doc_file}: {e}")
        
        jobs[job_id]["progress"] = f"Found {len(doc_functions)} documented functions"
        
        # Step 4: Compare using HybridComparator
        jobs[job_id]["progress"] = "Comparing code vs documentation..."
        
        comparator = HybridComparator()
        all_issues = []
        verified_count = 0
        total_comparisons = 0
        
        # Match functions by name
        code_func_map = {f.name.lower(): f for f in code_functions}
        doc_func_map = {f.name.lower(): f for f in doc_functions}
        
        # Compare functions that exist in both code and docs
        for func_name in code_func_map.keys():
            if func_name in doc_func_map:
                total_comparisons += 1
                code_func = code_func_map[func_name]
                doc_func = doc_func_map[func_name]
                
                # Use hybrid comparator
                result = comparator.compare(code_func, doc_func)
                
                if result.matches:
                    verified_count += 1
                
                # Convert issues to dict format
                for issue in result.issues:
                    all_issues.append({
                        "severity": issue.severity,
                        "function": issue.function,
                        "issue": issue.issue,
                        "code_has": issue.code_has,
                        "docs_say": issue.docs_say,
                        "suggested_fix": issue.suggested_fix
                    })
        
        # Functions in code but not documented
        for func_name, code_func in code_func_map.items():
            if func_name not in doc_func_map:
                all_issues.append({
                    "severity": "medium",
                    "function": code_func.name,
                    "issue": "Function exists in code but is not documented",
                    "code_has": f"{code_func.name}({', '.join(p.name for p in code_func.parameters)})",
                    "docs_say": "No documentation found",
                    "suggested_fix": f"Add documentation for {code_func.name}()"
                })
        
        # Functions documented but not in code
        for func_name, doc_func in doc_func_map.items():
            if func_name not in code_func_map:
                all_issues.append({
                    "severity": "high",
                    "function": doc_func.name,
                    "issue": "Function is documented but does not exist in code",
                    "code_has": "Function not found in code",
                    "docs_say": f"{doc_func.name}({', '.join(p.name for p in doc_func.parameters)})",
                    "suggested_fix": f"Remove documentation for {doc_func.name}() or check if function was renamed"
                })
        
        # Calculate trust score
        if total_comparisons > 0:
            trust_score = int((verified_count / total_comparisons) * 100)
        else:
            trust_score = 0
        
        # Return final results
        jobs[job_id]["status"] = JobStatus.COMPLETE
        jobs[job_id]["result"] = {
            "trust_score": trust_score,
            "total_functions": len(code_functions),
            "documented_functions": len(doc_functions),
            "verified": verified_count,
            "issues": all_issues,
            "files_analyzed": {
                "code_files": len(files['code']),
                "doc_files": len(files['docs'])
            },
            "stats": {
                "functions_in_code": len(code_functions),
                "functions_in_docs": len(doc_functions),
                "functions_compared": total_comparisons,
                "functions_matched": verified_count,
                "undocumented_functions": len(code_functions) - total_comparisons,
                "orphaned_docs": len(doc_functions) - total_comparisons
            }
        }
        
        cleanup_repo(repo_path)
        print(f"✅ Analysis complete! Trust score: {trust_score}%")
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()
        jobs[job_id]["status"] = JobStatus.ERROR
        jobs[job_id]["error"] = str(e)

# ============= SERVER =============

if __name__ == "__main__":
    import uvicorn
    print("🚀 Veritas API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)