"""Chat router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.core.exceptions import NotFoundError
from api.dependencies import get_current_user, get_db
from api.models.chat import ChatMessageCreate, ChatMessageResponse, ChatSendMessageResponse, ChatSessionResponse
from api.services.chat_service import ChatService
from database.models import TopicField, User

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/topic-fields/{topic_field_id}/chat/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_or_get_chat_session(
    topic_field_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create or get chat session for a topic field.

    Args:
        topic_field_id: Topic field ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Chat session information

    Raises:
        HTTPException: If topic field not found
    """
    # Verify topic field exists
    topic_field = db.query(TopicField).filter(TopicField.id == topic_field_id).first()
    if not topic_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic field with id {topic_field_id} not found",
        )

    session = ChatService.get_or_create_session(
        user_id=current_user.id,
        topic_field_id=topic_field_id,
        db=db,
    )

    # Get message count
    message_count = len(ChatService.get_messages(session.id, db=db))

    return ChatSessionResponse(
        id=session.id,
        user_id=session.user_id,
        topic_field_id=session.topic_field_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        topic_field={
            "id": topic_field.id,
            "name": topic_field.name,
            "description": topic_field.description,
            "system_prompt": topic_field.system_prompt,
            "created_at": topic_field.created_at,
        },
        message_count=message_count,
    )


@router.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get chat messages for a session.

    Args:
        session_id: Session ID
        limit: Maximum number of messages
        offset: Pagination offset
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of chat messages

    Raises:
        HTTPException: If session not found or access denied
    """
    try:
        # Verify session belongs to user
        ChatService.get_session(session_id, current_user.id, db)

        messages = ChatService.get_messages(session_id, db=db, limit=limit, offset=offset)
        return [ChatMessageResponse.model_validate(msg) for msg in messages]
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/chat/sessions/{session_id}/messages", response_model=ChatSendMessageResponse)
async def send_chat_message(
    session_id: int,
    request: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a message in a chat session and get LLM response.

    Args:
        session_id: Session ID
        request: Message content
        current_user: Current authenticated user
        db: Database session

    Returns:
        User message and assistant response

    Raises:
        HTTPException: If session not found or access denied
    """
    try:
        # Verify session belongs to user
        session = ChatService.get_session(session_id, current_user.id, db)

        # Get topic field
        topic_field = db.query(TopicField).filter(TopicField.id == session.topic_field_id).first()
        if not topic_field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic field for session {session_id} not found",
            )

        # Send message
        chat_service = ChatService()
        user_message, assistant_message = chat_service.send_message(
            session_id=session_id,
            user_message_content=request.content,
            topic_field=topic_field,
            db=db,
        )

        return ChatSendMessageResponse(
            user_message=ChatMessageResponse.model_validate(user_message),
            assistant_message=ChatMessageResponse.model_validate(assistant_message),
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/users/me/chat/sessions", response_model=List[ChatSessionResponse])
async def get_user_chat_sessions(
    topic_field_id: Optional[int] = Query(None, description="Filter by topic field"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all chat sessions for current user.

    Args:
        topic_field_id: Optional filter by topic field
        limit: Maximum number of sessions
        offset: Pagination offset
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of chat sessions
    """
    from database.models import ChatSession

    query = db.query(ChatSession).filter(ChatSession.user_id == current_user.id)

    if topic_field_id:
        query = query.filter(ChatSession.topic_field_id == topic_field_id)

    sessions = query.order_by(ChatSession.updated_at.desc()).offset(offset).limit(limit).all()

    result = []
    for session in sessions:
        # Get message count
        message_count = len(ChatService.get_messages(session.id, db=db))

        # Get topic field
        topic_field = db.query(TopicField).filter(TopicField.id == session.topic_field_id).first()

        result.append(
            ChatSessionResponse(
                id=session.id,
                user_id=session.user_id,
                topic_field_id=session.topic_field_id,
                created_at=session.created_at,
                updated_at=session.updated_at,
                topic_field=(
                    {
                        "id": topic_field.id,
                        "name": topic_field.name,
                        "description": topic_field.description,
                        "system_prompt": topic_field.system_prompt,
                        "created_at": topic_field.created_at,
                    }
                    if topic_field
                    else None
                ),
                message_count=message_count,
            )
        )

    return result

