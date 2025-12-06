"""Example router demonstrating database usage."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.base import get_db

router = APIRouter(prefix="/api/v1", tags=["example"])


@router.get("/")
async def api_info():
    """API v1 information endpoint."""
    return {
        "version": "1.0.0",
        "api_name": "Uni Pilot API",
        "endpoints": {
            "example": "/api/v1/example",
            "health": "/health",
            "version": "/version",
            "docs": "/docs",
        },
    }


@router.get("/example")
async def example_endpoint(db: Session = Depends(get_db)):
    """Example endpoint demonstrating database dependency injection."""
    
    return {
        "message": "This is an example endpoint",
        "database_connected": db is not None,
    }


