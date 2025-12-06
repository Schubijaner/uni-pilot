"""Tests for Chat Service (with mocked LLM)."""

from unittest.mock import MagicMock, patch

import pytest

from api.services.chat_service import ChatService
from database.models import ChatMessage, ChatSession, TopicField


def test_get_or_create_session_create(test_db_session, test_user, test_topic_field):
    """Test creating a new chat session."""
    session = ChatService.get_or_create_session(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )

    assert session.id is not None
    assert session.user_id == test_user.id
    assert session.topic_field_id == test_topic_field.id


def test_get_or_create_session_existing(test_db_session, test_user, test_topic_field):
    """Test getting existing chat session."""
    # Create session first
    session1 = ChatService.get_or_create_session(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )
    session_id = session1.id

    # Get existing session
    session2 = ChatService.get_or_create_session(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )

    assert session2.id == session_id


def test_get_session(test_db_session, test_user, test_topic_field):
    """Test getting session by ID."""
    session = ChatService.get_or_create_session(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )

    retrieved_session = ChatService.get_session(session.id, test_user.id, test_db_session)
    assert retrieved_session.id == session.id


def test_get_session_not_found(test_db_session):
    """Test getting non-existent session."""
    from api.core.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        ChatService.get_session(99999, None, test_db_session)


def test_get_session_access_denied(test_db_session, test_user, test_topic_field):
    """Test getting session with wrong user ID."""
    from api.core.exceptions import NotFoundError
    from database.models import User

    # Create another user
    other_user = User(
        email="other@example.com",
        password_hash="hash",
        first_name="Other",
        last_name="User",
    )
    test_db_session.add(other_user)
    test_db_session.commit()

    session = ChatService.get_or_create_session(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )

    with pytest.raises(NotFoundError):
        ChatService.get_session(session.id, other_user.id, test_db_session)


def test_get_messages(test_db_session, test_user, test_topic_field):
    """Test getting chat messages."""
    session = ChatService.get_or_create_session(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )

    # Add messages
    message1 = ChatMessage(
        session_id=session.id,
        role="user",
        content="Hello",
    )
    message2 = ChatMessage(
        session_id=session.id,
        role="assistant",
        content="Hi there!",
    )
    test_db_session.add_all([message1, message2])
    test_db_session.commit()

    messages = ChatService.get_messages(session.id, test_db_session, limit=10, offset=0)

    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


def test_get_messages_with_limit(test_db_session, test_user, test_topic_field):
    """Test getting messages with limit."""
    session = ChatService.get_or_create_session(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )

    # Add multiple messages
    for i in range(5):
        message = ChatMessage(
            session_id=session.id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
        )
        test_db_session.add(message)
    test_db_session.commit()

    messages = ChatService.get_messages(session.id, test_db_session, limit=3, offset=0)
    assert len(messages) == 3


@patch("api.services.chat_service.LLMService")
def test_send_message_mock_llm(mock_llm_service_class, test_db_session, test_user, test_topic_field):
    """Test sending message with mocked LLM service."""
    # Setup mock LLM service
    mock_llm_service = MagicMock()
    mock_llm_service.chat.return_value = "This is a mock response from LLM"
    mock_llm_service_class.return_value = mock_llm_service

    session = ChatService.get_or_create_session(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )

    chat_service = ChatService(llm_service=mock_llm_service)
    user_message, assistant_message = chat_service.send_message(
        session_id=session.id,
        user_message_content="Test question?",
        topic_field=test_topic_field,
        db=test_db_session,
    )

    assert user_message.role == "user"
    assert user_message.content == "Test question?"
    assert assistant_message.role == "assistant"
    assert assistant_message.content == "This is a mock response from LLM"

    # Verify LLM service was called
    mock_llm_service.chat.assert_called_once()

