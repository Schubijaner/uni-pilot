"""Chat service for LLM-powered chat sessions."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from api.core.config import get_settings
from api.core.exceptions import NotFoundError
from api.prompts.chat_prompts import get_chat_system_prompt
from api.services.llm_service import LLMService
from database.models import ChatMessage, ChatSession, TopicField

logger = logging.getLogger(__name__)
settings = get_settings()


class ChatService:
    """Service for chat operations."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize chat service with optional LLM service."""
        self.llm_service = llm_service or LLMService()

    @staticmethod
    def get_or_create_session(user_id: int, topic_field_id: int, db: Session) -> ChatSession:
        """
        Get existing chat session or create a new one.

        Args:
            user_id: User ID
            topic_field_id: Topic field ID
            db: Database session

        Returns:
            ChatSession object
        """
        session = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id, ChatSession.topic_field_id == topic_field_id)
            .first()
        )

        if not session:
            session = ChatSession(user_id=user_id, topic_field_id=topic_field_id)
            db.add(session)
            db.commit()
            db.refresh(session)

        return session

    @staticmethod
    def get_session(session_id: int, user_id: Optional[int], db: Session) -> ChatSession:
        """
        Get chat session by ID.

        Args:
            session_id: Session ID
            user_id: Optional user ID to verify ownership
            db: Database session

        Returns:
            ChatSession object

        Raises:
            NotFoundError: If session not found or user mismatch
        """
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()

        if not session:
            raise NotFoundError(f"Chat session {session_id} not found", "SESSION_NOT_FOUND")

        if user_id is not None and session.user_id != user_id:
            raise NotFoundError("Chat session not accessible", "SESSION_ACCESS_DENIED")

        return session

    @staticmethod
    def get_messages(session_id: int, db: Session, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """
        Get chat messages for a session.

        Args:
            session_id: Session ID
            limit: Maximum number of messages to return
            offset: Offset for pagination
            db: Database session

        Returns:
            List of ChatMessage objects (sorted by created_at ascending)
        """
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return messages

    def send_message(
        self,
        session_id: int,
        user_message_content: str,
        topic_field: TopicField,
        db: Session,
    ) -> tuple[ChatMessage, ChatMessage]:
        """
        Send a user message and get LLM response.

        Args:
            session_id: Chat session ID
            user_message_content: User message content
            topic_field: Topic field for context
            db: Database session

        Returns:
            Tuple of (user_message, assistant_message)

        Raises:
            NotFoundError: If session not found
        """
        # Get session
        session = ChatService.get_session(session_id, None, db)

        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=user_message_content,
        )
        db.add(user_message)
        db.flush()

        # Get recent message history (for context)
        recent_messages = ChatService.get_messages(session_id, db=db, limit=settings.MAX_CHAT_HISTORY_MESSAGES)

        # Build message history for LLM (format: [{"role": "user", "content": "..."}, ...])
        llm_messages = []
        for msg in recent_messages:
            llm_messages.append({"role": msg.role, "content": msg.content})

        # Add current user message if not already in history
        if not recent_messages or recent_messages[-1].id != user_message.id:
            llm_messages.append({"role": "user", "content": user_message_content})

        # Get system prompt
        system_prompt = get_chat_system_prompt(topic_field)

        try:
            # Call LLM
            logger.info(f"Sending message to LLM for session {session_id}")
            assistant_content = self.llm_service.chat(
                system_prompt=system_prompt,
                messages=llm_messages,
                temperature=settings.CHAT_TEMPERATURE,
            )

            # Save assistant message
            assistant_message = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=assistant_content,
            )
            db.add(assistant_message)

            # Update session updated_at
            from datetime import datetime

            session.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(user_message)
            db.refresh(assistant_message)

            logger.info(f"Successfully processed message for session {session_id}")
            return user_message, assistant_message

        except Exception as e:
            logger.error(f"Failed to process chat message: {e}")
            db.rollback()
            raise

