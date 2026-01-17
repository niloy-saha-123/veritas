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
        "result": None
    }
    return JobResponse(job_id=job_id, status=JobStatus.PENDING)

@app.get("/results/{job_id}")
async def get_results(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}, 404
    return jobs[job_id]

if __name__ == "__main__":
    import uvicorn
    print("🚀 Veritas API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)