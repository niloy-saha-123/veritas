# Health check endpoints - /health and /status for monitoring API availability

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Veritas.dev API"
    }


@router.get("/status")
async def detailed_status():
    """
    Detailed status endpoint with system information.
    
    Returns:
        dict: Detailed system status
    """
    return {
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "healthy",
            "detection_engine": "ready",
            "integrations": "configured"
        }
    }
