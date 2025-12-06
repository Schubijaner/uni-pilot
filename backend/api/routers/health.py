"""Health check router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    from datetime import datetime, timezone

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "version": "1.0.0",
    }


@router.get("/version")
async def get_version():
    """Get API version."""
    return {
        "version": "1.0.0",
        "api_name": "Uni Pilot API",
    }


