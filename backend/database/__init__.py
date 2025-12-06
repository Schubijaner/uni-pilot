"""Database models and utilities for Uni Pilot."""

from database.base import Base, SessionLocal, create_tables, drop_tables, engine, get_db
from database.models import (
    CareerTreeRelationship,
    CareerTreeNode,
    ChatMessage,
    ChatSession,
    Module,
    ModuleImport,
    ModuleType,
    Recommendation,
    Roadmap,
    RoadmapItem,
    RoadmapItemType,
    StudyProgram,
    TopicField,
    University,
    User,
    UserModuleProgress,
    UserProfile,
    UserQuestion,
    UserRoadmapItem,
)

__all__ = [
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    "create_tables",
    "drop_tables",
    # Models
    "User",
    "UserProfile",
    "University",
    "StudyProgram",
    "Module",
    "ModuleType",
    "TopicField",
    "CareerTreeNode",
    "CareerTreeRelationship",
    "Roadmap",
    "RoadmapItem",
    "RoadmapItemType",
    "Recommendation",
    "ChatSession",
    "ChatMessage",
    "UserQuestion",
    "ModuleImport",
    "UserModuleProgress",
    "UserRoadmapItem",
]

