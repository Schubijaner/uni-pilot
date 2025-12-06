"""Career tree and topic field related Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TopicFieldResponse(BaseModel):
    """Topic field response model."""

    id: int
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CareerTreeNodeResponse(BaseModel):
    """Career tree node response model."""

    id: int
    name: str
    description: Optional[str] = None
    is_leaf: bool
    level: int
    topic_field: Optional[TopicFieldResponse] = None
    children: List["CareerTreeNodeResponse"] = []

    class Config:
        from_attributes = True


# Update forward reference for recursive model
CareerTreeNodeResponse.model_rebuild()


class CareerTreeResponse(BaseModel):
    """Career tree response (hierarchische Struktur)."""

    study_program_id: int
    nodes: Optional[CareerTreeNodeResponse] = None

    class Config:
        schema_extra = {
            "example": {
                "study_program_id": 1,
                "nodes": {
                    "id": 1,
                    "name": "Software Development",
                    "level": 1,
                    "is_leaf": False,
                    "children": [],
                },
            }
        }


class TopicFieldSelectRequest(BaseModel):
    """Request to select a topic field."""

    topic_field_id: int

    class Config:
        schema_extra = {
            "example": {
                "topic_field_id": 1,
            }
        }


class UserQuestionCreate(BaseModel):
    """User question creation request."""

    question_text: str
    answer: bool
    career_tree_node_id: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "question_text": "Interessierst du dich für Frontend-Entwicklung?",
                "answer": True,
                "career_tree_node_id": 2,
            }
        }


class UserQuestionResponse(BaseModel):
    """User question response model."""

    id: int
    user_id: int
    question_text: str
    answer: bool
    career_tree_node_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

