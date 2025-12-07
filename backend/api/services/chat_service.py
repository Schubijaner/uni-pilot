"""Chat service for LLM-powered chat sessions."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from api.core.config import get_settings
from api.core.exceptions import NotFoundError
from api.prompts.chat_prompts import (
    generate_job_greeting_prompt,
    generate_topic_field_greeting_prompt,
    get_chat_system_prompt,
    get_chat_system_prompt_for_job,
)
from api.services.llm_service import LLMService
from database.models import ChatMessage, ChatSession, TopicField, CareerTreeNode

logger = logging.getLogger(__name__)
settings = get_settings()


class ChatService:
    """Service for chat operations."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize chat service with optional LLM service."""
        self.llm_service = llm_service or LLMService()

    @staticmethod
    def get_or_create_session(
        user_id: int,
        topic_field_id: Optional[int] = None,
        career_tree_node_id: Optional[int] = None,
        db: Session = None,
    ) -> ChatSession:
        """
        Get existing chat session or create a new one.

        Args:
            user_id: User ID
            topic_field_id: Optional topic field ID (for backward compatibility)
            career_tree_node_id: Optional career tree node ID (job ID)
            db: Database session

        Returns:
            ChatSession object

        Raises:
            ValueError: If neither topic_field_id nor career_tree_node_id is provided
        """
        if not topic_field_id and not career_tree_node_id:
            raise ValueError("Either topic_field_id or career_tree_node_id must be provided")

        # Try to find existing session
        # For jobs: search by both topic_field_id and career_tree_node_id to ensure correct matching
        query = db.query(ChatSession).filter(ChatSession.user_id == user_id)
        
        if topic_field_id and career_tree_node_id:
            # For jobs: both fields must match
            query = query.filter(
                ChatSession.topic_field_id == topic_field_id,
                ChatSession.career_tree_node_id == career_tree_node_id,
            )
        elif topic_field_id:
            # For topic field only sessions
            query = query.filter(ChatSession.topic_field_id == topic_field_id)
        elif career_tree_node_id:
            # For legacy job sessions (backward compatibility)
            query = query.filter(ChatSession.career_tree_node_id == career_tree_node_id)

        session = query.first()

        if not session:
            session = ChatSession(
                user_id=user_id,
                topic_field_id=topic_field_id,
                career_tree_node_id=career_tree_node_id,
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        return session

    def get_or_create_job_session(self, user_id: int, job_id: int, db: Session) -> ChatSession:
        """
        Get existing chat session for a job or create a new one.
        
        Also sets the job's topic_field_id to connect the chat session with the roadmap.
        If a new session is created, generates and stores a job-specific greeting.

        Args:
            user_id: User ID
            job_id: Career tree node ID (job, must be a leaf node)
            db: Database session

        Returns:
            ChatSession object
        """
        # Get job to access its topic_field_id
        job = db.query(CareerTreeNode).filter(CareerTreeNode.id == job_id).first()
        if not job:
            raise NotFoundError(f"Career tree node with id {job_id} not found", "JOB_NOT_FOUND")
        
        if not job.is_leaf:
            raise NotFoundError(
                f"Career tree node with id {job_id} is not a leaf node (job)",
                "NOT_A_JOB",
            )
        
        # Use topic_field_id from job to connect chat session with roadmap
        topic_field_id = job.topic_field_id
        
        # Create or get session
        session = ChatService.get_or_create_session(
            user_id=user_id,
            topic_field_id=topic_field_id,  # Connect to roadmap via topic_field_id
            career_tree_node_id=job_id,  # Keep job reference
            db=db,
        )
        
        # Check if there are any messages - if not, generate greeting
        existing_messages = ChatService.get_messages(session.id, db=db, limit=1)
        if not existing_messages:
            try:
                self._generate_and_store_greeting(session.id, job, db)
            except Exception as e:
                # Log error but don't fail session creation
                logger.error(
                    f"Failed to generate greeting for job session {session.id}: {e}. "
                    f"Session created without greeting."
                )
        
        return session

    def get_or_create_topic_field_session(
        self, user_id: int, topic_field_id: int, db: Session
    ) -> ChatSession:
        """
        Get existing chat session for a topic field or create a new one.
        
        If a new session is created or existing session has no messages, generates and stores a topic-field-specific greeting.

        Args:
            user_id: User ID
            topic_field_id: Topic field ID
            db: Database session

        Returns:
            ChatSession object
        """
        # Get topic field
        topic_field = db.query(TopicField).filter(TopicField.id == topic_field_id).first()
        if not topic_field:
            raise NotFoundError(f"Topic field with id {topic_field_id} not found", "TOPIC_FIELD_NOT_FOUND")

        # Create or get session
        session = ChatService.get_or_create_session(
            user_id=user_id,
            topic_field_id=topic_field_id,
            db=db,
        )

        # Check if there are any messages - if not, generate greeting
        existing_messages = ChatService.get_messages(session.id, db=db, limit=1)
        if not existing_messages:
            try:
                self._generate_and_store_topic_field_greeting(session.id, topic_field, db)
            except Exception as e:
                # Log error but don't fail session creation
                logger.error(
                    f"Failed to generate greeting for topic field session {session.id}: {e}. "
                    f"Session created without greeting."
                )

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

    def _generate_and_store_greeting(
        self,
        session_id: int,
        job: CareerTreeNode,
        db: Session,
    ) -> ChatMessage:
        """
        Generate and store a greeting message for a new job chat session.

        Args:
            session_id: Chat session ID
            job: Career tree node (job)
            db: Database session

        Returns:
            ChatMessage object with the greeting

        Note:
            If LLM generation fails, a fallback greeting is used.
        """
        try:
            # Generate greeting prompt
            greeting_prompt = generate_job_greeting_prompt(job)

            # Call LLM with higher temperature for creativity
            logger.info(f"Generating greeting for job chat session {session_id} (job: {job.name})")
            greeting_content = self.llm_service.chat(
                system_prompt="Du bist ein kreativer Texter, der witzige und einladende Begrüßungen für Chat-Assistenten schreibt.",
                messages=[{"role": "user", "content": greeting_prompt}],
                temperature=0.9,  # Higher temperature for more creativity
                max_tokens=200,  # Short greeting
            )

            # Clean up the greeting (remove any extra formatting)
            greeting_content = greeting_content.strip()

        except Exception as e:
            logger.warning(
                f"Failed to generate LLM greeting for session {session_id}: {e}. Using fallback greeting."
            )
            # Fallback greeting
            job_name = job.name
            greeting_content = f"""Hallo! 👋 Ich bin dein persönlicher Assistent für den Beruf "{job_name}".

Ich helfe dir dabei, alles über diesen spannenden Karriereweg zu erfahren - von den benötigten Skills über Tools und Technologien bis hin zu Einstiegsmöglichkeiten.

Worüber möchtest du mehr erfahren?"""

        # Save greeting as assistant message
        greeting_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=greeting_content,
        )
        db.add(greeting_message)
        db.commit()
        db.refresh(greeting_message)

        logger.info(f"Successfully stored greeting for session {session_id}")
        return greeting_message

    def _generate_and_store_topic_field_greeting(
        self,
        session_id: int,
        topic_field: TopicField,
        db: Session,
    ) -> ChatMessage:
        """
        Generate and store a greeting message for a new topic field chat session.

        Args:
            session_id: Chat session ID
            topic_field: Topic field
            db: Database session

        Returns:
            ChatMessage object with the greeting

        Note:
            If LLM generation fails, a fallback greeting is used.
        """
        try:
            # Generate greeting prompt
            greeting_prompt = generate_topic_field_greeting_prompt(topic_field)

            # Call LLM with higher temperature for creativity
            logger.info(f"Generating greeting for topic field chat session {session_id} (topic: {topic_field.name})")
            greeting_content = self.llm_service.chat(
                system_prompt="Du bist ein kreativer Texter, der witzige und einladende Begrüßungen für Chat-Assistenten schreibt.",
                messages=[{"role": "user", "content": greeting_prompt}],
                temperature=0.9,  # Higher temperature for more creativity
                max_tokens=200,  # Short greeting
            )

            # Clean up the greeting (remove any extra formatting)
            greeting_content = greeting_content.strip()

        except Exception as e:
            logger.warning(
                f"Failed to generate LLM greeting for session {session_id}: {e}. Using fallback greeting."
            )
            # Fallback greeting
            topic_name = topic_field.name
            greeting_content = f"""Hallo! 👋 Ich bin dein persönlicher Assistent für das Themenfeld "{topic_name}".

Ich helfe dir dabei, alles über dieses spannende Themenfeld zu erfahren - von den benötigten Skills über Tools und Technologien bis hin zu Einstiegsmöglichkeiten.

Worüber möchtest du mehr erfahren?"""

        # Save greeting as assistant message
        greeting_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=greeting_content,
        )
        db.add(greeting_message)
        db.commit()
        db.refresh(greeting_message)

        logger.info(f"Successfully stored greeting for session {session_id}")
        return greeting_message

    def send_message(
        self,
        session_id: int,
        user_message_content: str,
        topic_field: Optional[TopicField] = None,
        job: Optional[CareerTreeNode] = None,
        db: Session = None,
    ) -> tuple[ChatMessage, ChatMessage]:
        """
        Send a user message and get LLM response.

        Args:
            session_id: Chat session ID
            user_message_content: User message content
            topic_field: Optional topic field for context (for backward compatibility)
            job: Optional job (career tree node) for context
            db: Database session

        Returns:
            Tuple of (user_message, assistant_message)

        Raises:
            NotFoundError: If session not found
            ValueError: If neither topic_field nor job is provided
        """
        # Get session
        session = ChatService.get_session(session_id, None, db)

        # Determine context (prefer job over topic_field)
        if not job and session.career_tree_node_id:
            job = db.query(CareerTreeNode).filter(CareerTreeNode.id == session.career_tree_node_id).first()
        if not topic_field and session.topic_field_id:
            topic_field = db.query(TopicField).filter(TopicField.id == session.topic_field_id).first()

        if not job and not topic_field:
            raise ValueError("Session must have either a job or topic_field")

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

        # Get system prompt (prefer job-based prompt)
        if job:
            system_prompt = get_chat_system_prompt_for_job(job)
        else:
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

