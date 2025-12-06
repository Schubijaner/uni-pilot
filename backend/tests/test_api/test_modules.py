"""Tests for Modules API endpoints."""

import pytest


def test_get_modules_by_study_program(client, test_study_program, test_module):
    """Test getting modules by study program."""
    response = client.get(f"/api/v1/study-programs/{test_study_program.id}/modules")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


def test_get_modules_study_program_not_found_404(client):
    """Test getting modules for non-existent study program."""
    response = client.get("/api/v1/study-programs/99999/modules")

    assert response.status_code == 404


def test_get_modules_filter_by_type(client, test_study_program, test_module):
    """Test getting modules filtered by type."""
    from database.models import Module, ModuleType

    # Create another module with different type
    # Note: test_module is REQUIRED by default in fixture
    response = client.get(
        f"/api/v1/study-programs/{test_study_program.id}/modules?module_type=REQUIRED"
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # All items should be REQUIRED type
    for item in data["items"]:
        assert item["module_type"] == "REQUIRED"


def test_get_modules_filter_by_semester(client, test_study_program, test_module):
    """Test getting modules filtered by semester."""
    response = client.get(
        f"/api/v1/study-programs/{test_study_program.id}/modules?semester={test_module.semester}"
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # All items should be in the specified semester
    for item in data["items"]:
        if item.get("semester") is not None:
            assert item["semester"] == test_module.semester


def test_get_modules_pagination(client, test_study_program):
    """Test getting modules with pagination."""
    response = client.get(
        f"/api/v1/study-programs/{test_study_program.id}/modules?limit=1&offset=0"
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "limit" in data
    assert "offset" in data
    assert data["limit"] == 1
    assert data["offset"] == 0


def test_get_modules_invalid_module_type_400(client, test_study_program):
    """Test getting modules with invalid module type filter."""
    response = client.get(
        f"/api/v1/study-programs/{test_study_program.id}/modules?module_type=INVALID"
    )

    assert response.status_code == 400

