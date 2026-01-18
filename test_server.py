# test_server.py - Quick environment test
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="P3 Test Server")

@app.get("/")
def root():
    return {"message": "P3 is ready!", "status": "working"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "veritas-test",
        "p3": "environment verified"
    }

if __name__ == "__main__":
    print("🚀 Starting P3 test server...")
    print("📍 Visit: http://localhost:8000")
    print("📍 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)