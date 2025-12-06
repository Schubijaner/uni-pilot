"""Tests for Auth Service."""

import pytest

from api.core.exceptions import AuthenticationError, ValidationError
from api.services.auth_service import AuthService
from database.models import User


def test_register_user_success(test_db_session):
    """Test successful user registration."""
    user = AuthService.register_user(
        email="newuser@example.com",
        password="password123",
        first_name="New",
        last_name="User",
        db=test_db_session,
    )

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.first_name == "New"
    assert user.last_name == "User"
    assert user.password_hash is not None
    assert user.password_hash != "password123"  # Should be hashed


def test_register_user_duplicate_email(test_db_session, test_user):
    """Test registration with duplicate email."""
    with pytest.raises(ValidationError) as exc_info:
        AuthService.register_user(
            email=test_user.email,  # Same email as test_user
            password="password123",
            first_name="Duplicate",
            last_name="User",
            db=test_db_session,
        )

    assert "already registered" in exc_info.value.message.lower()


def test_authenticate_user_success(test_db_session, test_user):
    """Test successful user authentication."""
    from api.core.security import verify_password

    authenticated_user = AuthService.authenticate_user(
        email=test_user.email,
        password="testpassword123",  # Password from test_user fixture
        db=test_db_session,
    )

    assert authenticated_user is not None
    assert authenticated_user.id == test_user.id
    assert authenticated_user.email == test_user.email
    assert verify_password("testpassword123", authenticated_user.password_hash)


def test_authenticate_user_wrong_password(test_db_session, test_user):
    """Test authentication with wrong password."""
    authenticated_user = AuthService.authenticate_user(
        email=test_user.email,
        password="wrongpassword",
        db=test_db_session,
    )

    assert authenticated_user is None


def test_authenticate_user_not_found(test_db_session):
    """Test authentication with non-existent user."""
    authenticated_user = AuthService.authenticate_user(
        email="nonexistent@example.com",
        password="password123",
        db=test_db_session,
    )

    assert authenticated_user is None


def test_create_token_for_user(test_user):
    """Test JWT token creation for user."""
    token = AuthService.create_token_for_user(test_user)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

    # Verify token can be decoded
    from api.core.security import decode_token

    payload = decode_token(token)
    assert int(payload.get("sub")) == test_user.id  # sub is stored as string in JWT


def test_login_user_success(test_db_session, test_user):
    """Test successful user login."""
    user, token = AuthService.login_user(
        email=test_user.email,
        password="testpassword123",
        db=test_db_session,
    )

    assert user.id == test_user.id
    assert token is not None
    assert isinstance(token, str)

    # Verify token
    from api.core.security import decode_token

    payload = decode_token(token)
    assert int(payload.get("sub")) == test_user.id  # sub is stored as string in JWT


def test_login_user_invalid_credentials(test_db_session, test_user):
    """Test login with invalid credentials."""
    with pytest.raises(AuthenticationError) as exc_info:
        AuthService.login_user(
            email=test_user.email,
            password="wrongpassword",
            db=test_db_session,
        )

    assert "invalid" in exc_info.value.message.lower() or "credential" in exc_info.value.message.lower()


def test_login_user_not_found(test_db_session):
    """Test login with non-existent user."""
    with pytest.raises(AuthenticationError):
        AuthService.login_user(
            email="nonexistent@example.com",
            password="password123",
            db=test_db_session,
        )

