"""Authentication-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securePassword123",
                "first_name": "Max",
                "last_name": "Mustermann",
            }
        }


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securePassword123",
            }
        }


class UserResponse(BaseModel):
    """User response model."""

    id: int
    email: str
    first_name: str
    last_name: str
    created_at: datetime

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "first_name": "Max",
                "last_name": "Mustermann",
                "created_at": "2024-01-15T10:30:00Z",
            }
        }


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "first_name": "Max",
                    "last_name": "Mustermann",
                    "created_at": "2024-01-15T10:30:00Z",
                },
            }
        }

