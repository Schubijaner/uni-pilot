"""Tests for Onboarding API endpoints."""

import pytest


def test_get_universities(client, test_university):
    """Test getting all universities."""
    response = client.get("/api/v1/universities")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


def test_get_universities_with_search(client, test_university):
    """Test getting universities with search."""
    response = client.get("/api/v1/universities?search=Test")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)


def test_get_study_programs_by_university(client, test_university, test_study_program):
    """Test getting study programs by university."""
    response = client.get(f"/api/v1/universities/{test_university.id}/study-programs")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


def test_get_study_programs_university_not_found_404(client):
    """Test getting study programs for non-existent university."""
    response = client.get("/api/v1/universities/99999/study-programs")

    assert response.status_code == 404


def test_get_career_tree(client, test_study_program):
    """Test getting career tree."""
    response = client.get(f"/api/v1/study-programs/{test_study_program.id}/career-tree")

    assert response.status_code == 200
    data = response.json()
    assert data["study_program_id"] == test_study_program.id
    assert "nodes" in data


def test_get_career_tree_not_found_404(client):
    """Test getting career tree for non-existent study program."""
    response = client.get("/api/v1/study-programs/99999/career-tree")

    assert response.status_code == 404


def test_get_topic_fields(client, test_topic_field):
    """Test getting all topic fields."""
    response = client.get("/api/v1/topic-fields")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_topic_field(client, test_topic_field):
    """Test getting topic field by ID."""
    response = client.get(f"/api/v1/topic-fields/{test_topic_field.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_topic_field.id
    assert data["name"] == test_topic_field.name


def test_get_topic_field_not_found_404(client):
    """Test getting non-existent topic field."""
    response = client.get("/api/v1/topic-fields/99999")

    assert response.status_code == 404


def test_select_topic_field(authenticated_client, test_user, test_topic_field):
    """Test selecting topic field."""
    from database.models import UserProfile

    # Create profile first
    authenticated_client.put(
        "/api/v1/users/me/profile",
        json={
            "current_semester": 3,
        },
    )

    response = authenticated_client.put(
        "/api/v1/users/me/profile/topic-field",
        json={
            "topic_field_id": test_topic_field.id,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["selected_topic_field_id"] == test_topic_field.id


def test_create_user_question(authenticated_client, test_user, test_career_tree_node):
    """Test creating user question."""
    from api.models.career import UserQuestionCreate

    response = authenticated_client.post(
        "/api/v1/users/me/questions",
        json={
            "question_text": "Are you interested in frontend?",
            "answer": True,
            "career_tree_node_id": test_career_tree_node.id,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["question_text"] == "Are you interested in frontend?"
    assert data["answer"] is True


def test_get_user_questions(authenticated_client, test_user):
    """Test getting user questions."""
    response = authenticated_client.get("/api/v1/users/me/questions")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

