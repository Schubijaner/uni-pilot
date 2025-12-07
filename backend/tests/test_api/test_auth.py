"""Tests for Auth API endpoints."""

import pytest


def test_register_endpoint(client, test_db_session):
    """Test user registration endpoint."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert "id" in data


def test_register_duplicate_email_400(client, test_user):
    """Test registration with duplicate email."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,  # Duplicate email
            "password": "password123",
            "first_name": "Duplicate",
            "last_name": "User",
        },
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower() or "email" in response.json()["detail"].lower()


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email
    assert data["user"]["id"] == test_user.id


def test_login_invalid_credentials_401(client, test_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower() or "credential" in response.json()["detail"].lower()


def test_login_user_not_found_401(client):
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401


def test_get_current_user(authenticated_client, test_user):
    """Test getting current user information."""
    response = authenticated_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_login_with_json_format(client, test_user):
    """Test login with JSON format (standard)."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "testuser@example.com"


def test_login_with_form_data_format(client, test_user):
    """Test login with OAuth2 form-data format."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",  # OAuth2 uses "username" for email
            "password": "TestPassword123!",
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "testuser@example.com"


def test_login_form_data_invalid_credentials(client, test_user):
    """Test login with form-data format and invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "WrongPassword123!",
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower() or "credential" in response.json()["detail"].lower()


def test_login_form_data_missing_fields(client):
    """Test login with form-data format missing required fields."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",
            # Missing password
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 422


def test_login_with_roadmap_credentials_json(client, test_db_session):
    """Test login with credentials from 05-roadmaps.http using JSON format."""
    from api.core.security import hash_password
    from database.models import User

    # Create user with credentials from 05-roadmaps.http
    user = User(
        email="testuser@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="User",
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)

    # Test login with JSON format
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["id"] == user.id


def test_login_with_roadmap_credentials_form_data(client, test_db_session):
    """Test login with credentials from 05-roadmaps.http using OAuth2 form-data format."""
    from api.core.security import hash_password
    from database.models import User

    # Create user with credentials from 05-roadmaps.http
    user = User(
        email="testuser@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="User",
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)

    # Test login with OAuth2 form-data format
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",  # OAuth2 uses "username" for email
            "password": "TestPassword123!",
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["id"] == user.id

