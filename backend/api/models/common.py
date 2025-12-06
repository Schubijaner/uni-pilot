"""Common Pydantic schemas used across the API."""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    limit: int = 100
    offset: int = 0

    class Config:
        schema_extra = {
            "example": {
                "limit": 100,
                "offset": 0,
            }
        }


class PaginationResponse(BaseModel, Generic[T]):
    """Pagination response wrapper."""

    items: List[T]
    total: int
    limit: int
    offset: int
    has_more: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "limit": 100,
                "offset": 0,
                "has_more": False,
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response format."""

    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "detail": "Error description",
                "error_code": "ERROR_CODE",
                "timestamp": "2024-01-15T13:00:00Z",
            }
        }

