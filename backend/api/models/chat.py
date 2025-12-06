"""Chat-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from api.models.career import TopicFieldResponse


class ChatMessageCreate(BaseModel):
    """Chat message creation request."""

    content: str

    class Config:
        schema_extra = {
            "example": {
                "content": "Welche Skills brauche ich für Full Stack Development?",
            }
        }


class ChatMessageResponse(BaseModel):
    """Chat message response model."""

    id: int
    session_id: int
    role: str  # 'user' or 'assistant'
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSendMessageResponse(BaseModel):
    """Response after sending a chat message."""

    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse

    class Config:
        schema_extra = {
            "example": {
                "user_message": {
                    "id": 3,
                    "session_id": 1,
                    "role": "user",
                    "content": "Welche Tools empfehlst du?",
                    "created_at": "2024-01-15T12:10:00Z",
                },
                "assistant_message": {
                    "id": 4,
                    "session_id": 1,
                    "role": "assistant",
                    "content": "Für Backend-Entwicklung empfehle ich...",
                    "created_at": "2024-01-15T12:10:02Z",
                },
            }
        }


class ChatSessionResponse(BaseModel):
    """Chat session response model."""

    id: int
    user_id: int
    topic_field_id: int
    created_at: datetime
    updated_at: datetime
    topic_field: Optional[TopicFieldResponse] = None
    message_count: Optional[int] = None

    class Config:
        from_attributes = True

