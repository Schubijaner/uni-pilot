"""Helper utilities for test data factory functions."""

from database.models import (
    CareerTreeNode,
    Module,
    ModuleType,
    Roadmap,
    RoadmapItem,
    RoadmapItemType,
    StudyProgram,
    TopicField,
    University,
    User,
    UserProfile,
)
from api.core.security import hash_password


def create_test_user(db, email: str = "test@example.com", password: str = "password123", **kwargs):
    """Factory function to create a test user."""
    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=kwargs.get("first_name", "Test"),
        last_name=kwargs.get("last_name", "User"),
    )
    db.add(user)
    db.flush()
    return user


def create_test_university(db, name: str = "Test University", **kwargs):
    """Factory function to create a test university."""
    university = University(
        name=name,
        abbreviation=kwargs.get("abbreviation", "TU"),
    )
    db.add(university)
    db.flush()
    return university


def create_test_study_program(db, university_id: int, name: str = "Test Study Program", **kwargs):
    """Factory function to create a test study program."""
    study_program = StudyProgram(
        university_id=university_id,
        name=name,
        degree_type=kwargs.get("degree_type", "Bachelor"),
    )
    db.add(study_program)
    db.flush()
    return study_program


def create_test_module(db, study_program_id: int, name: str = "Test Module", **kwargs):
    """Factory function to create a test module."""
    module = Module(
        study_program_id=study_program_id,
        name=name,
        description=kwargs.get("description", "A test module"),
        module_type=kwargs.get("module_type", ModuleType.REQUIRED),
        semester=kwargs.get("semester", 1),
    )
    db.add(module)
    db.flush()
    return module


def create_test_topic_field(db, name: str = "Test Topic Field", **kwargs):
    """Factory function to create a test topic field."""
    topic_field = TopicField(
        name=name,
        description=kwargs.get("description", "A test topic field"),
        system_prompt=kwargs.get("system_prompt", "You are an expert in this field."),
    )
    db.add(topic_field)
    db.flush()
    return topic_field


def create_test_roadmap(db, topic_field_id: int, name: str = "Test Roadmap", **kwargs):
    """Factory function to create a test roadmap (without LLM)."""
    roadmap = Roadmap(
        topic_field_id=topic_field_id,
        name=name,
        description=kwargs.get("description", "A test roadmap"),
    )
    db.add(roadmap)
    db.flush()

    # Optionally create roadmap items
    if kwargs.get("create_items", False):
        # Create a simple hierarchical structure
        root_item = RoadmapItem(
            roadmap_id=roadmap.id,
            parent_id=None,
            item_type=RoadmapItemType.SKILL,
            title="Root Item",
            description="Root roadmap item",
            semester=1,
            is_semester_break=False,
            order=1,
            level=0,
            is_leaf=False,
            is_career_goal=False,
            is_important=False,
        )
        db.add(root_item)
        db.flush()

        # Create leaf item (career goal)
        leaf_item = RoadmapItem(
            roadmap_id=roadmap.id,
            parent_id=root_item.id,
            item_type=RoadmapItemType.CAREER,
            title="Career Goal",
            description="A test career goal",
            semester=None,
            is_semester_break=False,
            order=1,
            level=1,
            is_leaf=True,
            is_career_goal=True,
            is_important=True,
        )
        db.add(leaf_item)

    db.commit()
    db.refresh(roadmap)
    return roadmap


def create_test_user_profile(db, user_id: int, **kwargs):
    """Factory function to create a test user profile."""
    profile = UserProfile(
        user_id=user_id,
        university_id=kwargs.get("university_id"),
        study_program_id=kwargs.get("study_program_id"),
        current_semester=kwargs.get("current_semester"),
        skills=kwargs.get("skills"),
        selected_topic_field_id=kwargs.get("selected_topic_field_id"),
    )
    db.add(profile)
    db.flush()
    return profile

