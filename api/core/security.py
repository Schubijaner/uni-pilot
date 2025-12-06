"""Security utilities for authentication and password hashing."""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from api.core.config import get_settings
from database.models import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing token data (typically user info)
        expires_delta: Optional expiration time delta. If not provided, uses default from settings.

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload as dictionary

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise JWTError("Invalid or expired token")


def get_current_user(token: str, db: Session) -> User:
    """
    Get current user from JWT token.

    Args:
        token: JWT token string
        db: Database session

    Returns:
        User object

    Raises:
        JWTError: If token is invalid
        ValueError: If user not found
    """
    payload = decode_token(token)
    user_id: int = payload.get("sub")  # 'sub' is standard JWT claim for subject (user ID)

    if user_id is None:
        raise ValueError("Token payload missing user ID")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ValueError("User not found")

    return user

