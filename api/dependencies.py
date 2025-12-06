"""FastAPI dependencies for authentication and database."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.core.exceptions import CredentialException
from api.core.security import decode_token
from database.base import get_db
from database.models import User

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")

        if user_id is None:
            raise CredentialException()

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise CredentialException()

        return user
    except Exception:
        raise CredentialException()
