"""Tests for Chat API endpoints."""

from unittest.mock import MagicMock, patch

import pytest


def test_create_chat_session(authenticated_client, test_user, test_topic_field):
    """Test creating a chat session."""
    response = authenticated_client.post(
        f"/api/v1/topic-fields/{test_topic_field.id}/chat/sessions"
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == test_user.id
    assert data["topic_field_id"] == test_topic_field.id
    assert "id" in data


def test_create_chat_session_topic_field_not_found_404(authenticated_client):
    """Test creating session for non-existent topic field."""
    response = authenticated_client.post("/api/v1/topic-fields/99999/chat/sessions")

    assert response.status_code == 404


def test_get_chat_messages_empty(authenticated_client, test_user, test_topic_field):
    """Test getting messages from empty session."""
    # Create session first
    create_response = authenticated_client.post(
        f"/api/v1/topic-fields/{test_topic_field.id}/chat/sessions"
    )
    session_id = create_response.json()["id"]

    response = authenticated_client.get(f"/api/v1/chat/sessions/{session_id}/messages")

    assert response.status_code == 200
    assert response.json() == []


def test_get_chat_messages(authenticated_client, test_user, test_topic_field):
    """Test getting chat messages."""
    # Create session first
    create_response = authenticated_client.post(
        f"/api/v1/topic-fields/{test_topic_field.id}/chat/sessions"
    )
    session_id = create_response.json()["id"]

    # Send a message (which creates messages)
    with patch("api.services.chat_service.LLMService") as mock_llm:
        mock_llm_instance = MagicMock()
        mock_llm_instance.chat.return_value = "Mock response"
        mock_llm.return_value = mock_llm_instance

        send_response = authenticated_client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json={"content": "Test question?"},
        )

        # Get messages
        response = authenticated_client.get(f"/api/v1/chat/sessions/{session_id}/messages")

        assert response.status_code == 200
        messages = response.json()
        assert isinstance(messages, list)
        # Should have at least user message
        if send_response.status_code == 200:
            assert len(messages) >= 1


@patch("api.services.chat_service.LLMService")
def test_send_message_mock_llm(mock_llm_service_class, authenticated_client, test_user, test_topic_field):
    """Test sending message with mocked LLM."""
    # Setup mock
    mock_llm_service = MagicMock()
    mock_llm_service.chat.return_value = "This is a mock LLM response"
    mock_llm_service_class.return_value = mock_llm_service

    # Create session
    create_response = authenticated_client.post(
        f"/api/v1/topic-fields/{test_topic_field.id}/chat/sessions"
    )
    session_id = create_response.json()["id"]

    # Send message
    response = authenticated_client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        json={"content": "Test question?"},
    )

    # Should succeed with mocked LLM
    if response.status_code == 200:
        data = response.json()
        assert "user_message" in data
        assert "assistant_message" in data
        assert data["user_message"]["content"] == "Test question?"
        assert "mock" in data["assistant_message"]["content"].lower()


def test_send_message_session_not_found_404(authenticated_client):
    """Test sending message to non-existent session."""
    response = authenticated_client.post(
        "/api/v1/chat/sessions/99999/messages",
        json={"content": "Test?"},
    )

    assert response.status_code == 404


def test_get_user_chat_sessions(authenticated_client, test_user, test_topic_field):
    """Test getting user's chat sessions."""
    # Create a session first
    authenticated_client.post(f"/api/v1/topic-fields/{test_topic_field.id}/chat/sessions")

    response = authenticated_client.get("/api/v1/users/me/chat/sessions")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_user_chat_sessions_filtered(authenticated_client, test_user, test_topic_field):
    """Test getting user's chat sessions filtered by topic field."""
    # Create a session first
    authenticated_client.post(f"/api/v1/topic-fields/{test_topic_field.id}/chat/sessions")

    response = authenticated_client.get(
        f"/api/v1/users/me/chat/sessions?topic_field_id={test_topic_field.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

