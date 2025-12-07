"""SQLAlchemy models for Uni Pilot database."""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.base import Base


# Enums
class ModuleType(PyEnum):
    REQUIRED = "REQUIRED"
    ELECTIVE = "ELECTIVE"


class RoadmapItemType(PyEnum):
    COURSE = "COURSE"
    MODULE = "MODULE"
    PROJECT = "PROJECT"
    SKILL = "SKILL"
    BOOK = "BOOK"
    CERTIFICATE = "CERTIFICATE"
    INTERNSHIP = "INTERNSHIP"
    BOOTCAMP = "BOOTCAMP"
    CAREER = "CAREER"  # Beruf (für Leaf Nodes mit is_career_goal = True)


# Models
class User(Base):
    """User model - Basis-Entität für alle Nutzer."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    user_questions = relationship("UserQuestion", back_populates="user", cascade="all, delete-orphan")
    module_progress = relationship("UserModuleProgress", back_populates="user", cascade="all, delete-orphan")
    roadmap_progress = relationship("UserRoadmapItem", back_populates="user", cascade="all, delete-orphan")


class University(Base):
    """University model - Universitäten."""

    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    abbreviation = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    study_programs = relationship("StudyProgram", back_populates="university", cascade="all, delete-orphan")
    user_profiles = relationship("UserProfile", back_populates="university")


class StudyProgram(Base):
    """StudyProgram model - Studiengänge."""

    __tablename__ = "study_programs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    degree_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    university = relationship("University", back_populates="study_programs")
    user_profiles = relationship("UserProfile", back_populates="study_program")
    modules = relationship("Module", back_populates="study_program", cascade="all, delete-orphan")
    career_tree_nodes = relationship("CareerTreeNode", back_populates="study_program", cascade="all, delete-orphan")


class TopicField(Base):
    """TopicField model - Karriere-Themenfelder."""

    __tablename__ = "topic_fields"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    career_tree_nodes = relationship("CareerTreeNode", back_populates="topic_field")
    roadmaps = relationship("Roadmap", back_populates="topic_field", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="topic_field")
    recommendations = relationship("Recommendation", back_populates="topic_field")


class UserProfile(Base):
    """UserProfile model - Erweiterte Profilinformationen."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="SET NULL"), nullable=True)
    study_program_id = Column(Integer, ForeignKey("study_programs.id", ondelete="SET NULL"), nullable=True)
    current_semester = Column(Integer, nullable=True)
    skills = Column(Text, nullable=True)
    selected_topic_field_id = Column(Integer, ForeignKey("topic_fields.id", ondelete="SET NULL"), nullable=True)
    selected_job_id = Column(Integer, ForeignKey("career_tree_nodes.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="profile")
    university = relationship("University", back_populates="user_profiles")
    study_program = relationship("StudyProgram", back_populates="user_profiles")
    selected_topic_field = relationship("TopicField")
    selected_job = relationship("CareerTreeNode", foreign_keys=[selected_job_id])


class Module(Base):
    """Module model - Module aus dem Modulhandbuch."""

    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    module_type = Column(Enum(ModuleType), nullable=False)
    study_program_id = Column(Integer, ForeignKey("study_programs.id", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    study_program = relationship("StudyProgram", back_populates="modules")
    roadmap_items = relationship("RoadmapItem", back_populates="module")
    module_progress = relationship("UserModuleProgress", back_populates="module", cascade="all, delete-orphan")
    module_imports = relationship("ModuleImport", back_populates="module", cascade="all, delete-orphan")


class CareerTreeNode(Base):
    """CareerTreeNode model - Knoten im hierarchischen Karrierebaum."""

    __tablename__ = "career_tree_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    study_program_id = Column(Integer, ForeignKey("study_programs.id", ondelete="CASCADE"), nullable=False)
    topic_field_id = Column(Integer, ForeignKey("topic_fields.id", ondelete="SET NULL"), nullable=True)
    is_leaf = Column(Boolean, default=False, nullable=False)
    level = Column(Integer, default=0, nullable=False)
    questions = Column(Text, nullable=True)  # JSON-String: Liste von Fragen, eine pro Kindknoten
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    study_program = relationship("StudyProgram", back_populates="career_tree_nodes")
    topic_field = relationship("TopicField", back_populates="career_tree_nodes")
    user_questions = relationship("UserQuestion", back_populates="career_tree_node")
    parent_relationships = relationship(
        "CareerTreeRelationship",
        foreign_keys="CareerTreeRelationship.child_id",
        back_populates="child",
        cascade="all, delete-orphan",
    )
    child_relationships = relationship(
        "CareerTreeRelationship",
        foreign_keys="CareerTreeRelationship.parent_id",
        back_populates="parent",
        cascade="all, delete-orphan",
    )


class CareerTreeRelationship(Base):
    """CareerTreeRelationship model - Zwischentabelle für hierarchische Career Tree Struktur."""

    __tablename__ = "career_tree_relationships"

    parent_id = Column(Integer, ForeignKey("career_tree_nodes.id", ondelete="CASCADE"), primary_key=True)
    child_id = Column(Integer, ForeignKey("career_tree_nodes.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    parent = relationship("CareerTreeNode", foreign_keys=[parent_id], back_populates="child_relationships")
    child = relationship("CareerTreeNode", foreign_keys=[child_id], back_populates="parent_relationships")


class Roadmap(Base):
    """Roadmap model - Roadmap für ein spezifisches Themenfeld."""

    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_field_id = Column(Integer, ForeignKey("topic_fields.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    topic_field = relationship("TopicField", back_populates="roadmaps")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapItem(Base):
    """RoadmapItem model - Einzelner Eintrag in einer Roadmap (hierarchisch strukturiert)."""

    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("roadmap_items.id", ondelete="CASCADE"), nullable=True)
    item_type = Column(Enum(RoadmapItemType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    semester = Column(Integer, nullable=False)  # MUST NEVER be null
    is_semester_break = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)  # Tiefe im Tree (0 = Root)
    is_leaf = Column(Boolean, default=False, nullable=False)  # Ist Endknoten (Beruf)?
    is_career_goal = Column(Boolean, default=False, nullable=False)  # Ist dieser Item ein Beruf (Ziel)?
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="SET NULL"), nullable=True)
    is_important = Column(Boolean, default=False, nullable=False)
    top_skills = Column(Text, nullable=True)  # JSON-String: Array of {"skill": str, "score": int} for leaf nodes
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    roadmap = relationship("Roadmap", back_populates="items")
    parent = relationship("RoadmapItem", remote_side=[id], backref="children")  # Self-referencing für Tree-Struktur
    module = relationship("Module", back_populates="roadmap_items")
    roadmap_progress = relationship("UserRoadmapItem", back_populates="roadmap_item", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="roadmap_item")


class Recommendation(Base):
    """Recommendation model - Empfehlungen für Kurse, Bücher, Projekte, Skills etc."""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roadmap_item_id = Column(Integer, ForeignKey("roadmap_items.id", ondelete="SET NULL"), nullable=True)
    topic_field_id = Column(Integer, ForeignKey("topic_fields.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    recommendation_type = Column(Enum(RoadmapItemType), nullable=False)
    url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    roadmap_item = relationship("RoadmapItem", back_populates="recommendations")
    topic_field = relationship("TopicField", back_populates="recommendations")


class ChatSession(Base):
    """ChatSession model - Chat-Session für ein spezifisches Themenfeld oder Job."""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_field_id = Column(Integer, ForeignKey("topic_fields.id", ondelete="CASCADE"), nullable=True)
    career_tree_node_id = Column(Integer, ForeignKey("career_tree_nodes.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    topic_field = relationship("TopicField", back_populates="chat_sessions")
    career_tree_node = relationship("CareerTreeNode", foreign_keys=[career_tree_node_id])
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    # Composite index hint (will be created via migration/__init__)
    __table_args__ = ({"sqlite_autoincrement": True},)


class ChatMessage(Base):
    """ChatMessage model - Einzelne Nachricht in einer Chat-Session."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class UserQuestion(Base):
    """UserQuestion model - Fragen, die der User beantwortet hat."""

    __tablename__ = "user_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    answer = Column(Boolean, nullable=False)
    career_tree_node_id = Column(Integer, ForeignKey("career_tree_nodes.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_questions")
    career_tree_node = relationship("CareerTreeNode", back_populates="user_questions")


class ModuleImport(Base):
    """ModuleImport model - Historie und Metadaten für den Import von Modulen."""

    __tablename__ = "module_imports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    import_source = Column(String(255), nullable=False)
    import_data = Column(Text, nullable=True)
    import_status = Column(String(50), nullable=False)  # 'success', 'partial', 'failed'
    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    imported_by = Column(String(100), nullable=True)

    # Relationships
    module = relationship("Module", back_populates="module_imports")


# Many-to-Many Zwischentabellen
class UserModuleProgress(Base):
    """UserModuleProgress model - Verfolgt den Fortschritt eines Users bei Modulen."""

    __tablename__ = "user_module_progress"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), primary_key=True)
    completed = Column(Boolean, default=False, nullable=False)
    grade = Column(String(10), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="module_progress")
    module = relationship("Module", back_populates="module_progress")


class UserRoadmapItem(Base):
    """UserRoadmapItem model - Verfolgt den Fortschritt eines Users bei Roadmap-Items."""

    __tablename__ = "user_roadmap_items"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    roadmap_item_id = Column(Integer, ForeignKey("roadmap_items.id", ondelete="CASCADE"), primary_key=True)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="roadmap_progress")
    roadmap_item = relationship("RoadmapItem", back_populates="roadmap_progress")

