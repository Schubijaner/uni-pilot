"""Authentication service for user registration and login."""

from datetime import timedelta
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.core.config import get_settings
from api.core.exceptions import AuthenticationError, ValidationError
from api.core.security import create_access_token, hash_password, verify_password
from database.models import User

settings = get_settings()


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def register_user(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        db: Session,
    ) -> User:
        """
        Register a new user.

        Args:
            email: User email
            password: Plain text password
            first_name: User first name
            last_name: User last name
            db: Database session

        Returns:
            Created User object

        Raises:
            ValidationError: If email already exists or validation fails
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValidationError("Email already registered", "EMAIL_EXISTS")

        # Hash password
        password_hash = hash_password(password)

        # Create user
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
        )

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValidationError("Email already registered", "EMAIL_EXISTS")
        except Exception as e:
            db.rollback()
            raise ValidationError(f"Failed to create user: {str(e)}", "REGISTRATION_FAILED")

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: Plain text password
            db: Database session

        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    @staticmethod
    def create_token_for_user(user: User) -> str:
        """
        Create JWT access token for user.

        Args:
            user: User object

        Returns:
            JWT token string
        """
        token_data = {"sub": user.id}  # 'sub' is standard JWT claim for subject (user ID)
        access_token = create_access_token(data=token_data)
        return access_token

    @staticmethod
    def login_user(email: str, password: str, db: Session) -> tuple[User, str]:
        """
        Login user and return user with access token.

        Args:
            email: User email
            password: Plain text password
            db: Database session

        Returns:
            Tuple of (User, access_token)

        Raises:
            AuthenticationError: If authentication fails
        """
        user = AuthService.authenticate_user(email, password, db)

        if not user:
            raise AuthenticationError("Invalid email or password", "INVALID_CREDENTIALS")

        token = AuthService.create_token_for_user(user)
        return user, token

