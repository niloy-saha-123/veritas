from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uuid
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
    
    # ✅ ENABLE BACKGROUND PROCESSING
    background_tasks.add_task(process_analysis, job_id, request.github_url)
    
    return JobResponse(job_id=job_id, status=JobStatus.PENDING)

@app.get("/results/{job_id}")
async def get_results(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}, 404
    return jobs[job_id]

# ============= NEW: BACKGROUND PROCESSING =============

async def process_analysis(job_id: str, github_url: str):
    """Background task to analyze repository."""
    jobs[job_id]["status"] = JobStatus.PROCESSING
    
    try:
        from app.utils.git_utils import clone_repo, discover_files, cleanup_repo
        from app.parsers.parser_factory import parse_code
        from app.parsers.markdown_parser import parse_markdown
        
        # Clone repo
        jobs[job_id]["progress"] = "Cloning repository..."
        repo_path = clone_repo(github_url)
        files = discover_files(repo_path)
        
        jobs[job_id]["progress"] = f"Found {len(files['code'])} code, {len(files['docs'])} docs"
        
        # Parse code files (multi-language!)
        jobs[job_id]["progress"] = "Parsing code..."
        code_functions = []
        
        for code_file in files['code']:
            try:
                with open(code_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    functions = parse_code(code_file, content)
                    
                    for func in functions:
                        func.filepath = code_file
                    
                    code_functions.extend(functions)
            except Exception as e:
                print(f"Error: {code_file}: {e}")
        
        jobs[job_id]["progress"] = f"Parsed {len(code_functions)} functions"
        
        # Parse docs
        jobs[job_id]["progress"] = "Parsing docs..."
        doc_functions = []
        
        for doc_file in files['docs']:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    docs = parse_markdown(f.read())
                    doc_functions.extend(docs)
            except Exception as e:
                print(f"Error: {doc_file}: {e}")
        
        jobs[job_id]["progress"] = f"Found {len(doc_functions)} documented functions"
        
        # TODO: Step 4 - Compare (waiting for P2)
        
        # Return results
        jobs[job_id]["status"] = JobStatus.COMPLETE
        jobs[job_id]["result"] = {
            "trust_score": 0,
            "total_functions": len(code_functions),
            "documented_functions": len(doc_functions),
            "verified": 0,
            "issues": [],
            "files_analyzed": {
                "code": len(files['code']),
                "docs": len(files['docs'])
            }
        }
        
        cleanup_repo(repo_path)
        
    except Exception as e:
        jobs[job_id]["status"] = JobStatus.ERROR
        jobs[job_id]["error"] = str(e)

# ============= SERVER =============

if __name__ == "__main__":
    import uvicorn
    print("🚀 Veritas API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)