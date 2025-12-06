"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.exceptions import AuthenticationError, ValidationError
from api.dependencies import get_current_user, get_db
from api.models.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from api.services.auth_service import AuthService
from database.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Args:
        request: Registration request with email, password, name
        db: Database session

    Returns:
        Created user information

    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        user = AuthService.register_user(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            db=db,
        )
        return UserResponse.model_validate(user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in register_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login user and get JWT token.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        JWT token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        user, token = AuthService.login_user(
            email=request.email,
            password=request.password,
            db=db,
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user (from dependency)
        db: Database session

    Returns:
        Current user information with profile
    """
    return UserResponse.model_validate(current_user)

