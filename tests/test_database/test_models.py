"""Tests for SQLAlchemy models."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.models import (
    CareerTreeNode,
    Module,
    ModuleType,
    RoadmapItem,
    RoadmapItemType,
    StudyProgram,
    TopicField,
    University,
    User,
    UserProfile,
)


def test_user_creation(test_db_session):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
    )
    test_db_session.add(user)
    test_db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"


def test_user_unique_email_constraint(test_db_session):
    """Test that email must be unique."""
    user1 = User(
        email="duplicate@example.com",
        password_hash="hash1",
        first_name="First",
        last_name="User",
    )
    test_db_session.add(user1)
    test_db_session.commit()

    user2 = User(
        email="duplicate@example.com",
        password_hash="hash2",
        first_name="Second",
        last_name="User",
    )
    test_db_session.add(user2)

    with pytest.raises(IntegrityError):
        test_db_session.commit()


def test_user_profile_relationship(test_db_session, test_user, test_university, test_study_program):
    """Test User -> UserProfile relationship."""
    profile = UserProfile(
        user_id=test_user.id,
        university_id=test_university.id,
        study_program_id=test_study_program.id,
        current_semester=3,
        skills="Python, JavaScript",
    )
    test_db_session.add(profile)
    test_db_session.commit()

    # Test relationship
    assert test_user.profile is not None
    assert test_user.profile.user_id == test_user.id
    assert test_user.profile.university_id == test_university.id
    assert test_user.profile.study_program_id == test_study_program.id


def test_university_creation(test_db_session):
    """Test creating a university."""
    university = University(
        name="Test University",
        abbreviation="TU",
    )
    test_db_session.add(university)
    test_db_session.commit()

    assert university.id is not None
    assert university.name == "Test University"
    assert university.abbreviation == "TU"


def test_study_program_relationship(test_db_session, test_university):
    """Test University -> StudyProgram relationship."""
    from database.models import StudyProgram

    study_program = StudyProgram(
        university_id=test_university.id,
        name="Informatik",
        degree_type="Bachelor",
    )
    test_db_session.add(study_program)
    test_db_session.commit()

    assert study_program.university_id == test_university.id
    # Refresh to load relationship
    test_db_session.refresh(study_program)
    assert study_program.university is not None  # Relationship attribute


def test_module_creation(test_db_session, test_study_program):
    """Test creating a module."""
    from database.models import Module

    module = Module(
        study_program_id=test_study_program.id,
        name="Datenbanken",
        description="Grundlagen relationaler Datenbanken",
        module_type=ModuleType.REQUIRED,
        semester=3,
    )
    test_db_session.add(module)
    test_db_session.commit()

    assert module.id is not None
    assert module.name == "Datenbanken"
    assert module.module_type == ModuleType.REQUIRED
    assert module.semester == 3


def test_module_type_enum():
    """Test ModuleType enum values."""
    assert ModuleType.REQUIRED.value == "REQUIRED"
    assert ModuleType.ELECTIVE.value == "ELECTIVE"


def test_roadmap_item_type_enum():
    """Test RoadmapItemType enum values."""
    assert RoadmapItemType.COURSE.value == "COURSE"
    assert RoadmapItemType.MODULE.value == "MODULE"
    assert RoadmapItemType.PROJECT.value == "PROJECT"
    assert RoadmapItemType.SKILL.value == "SKILL"
    assert RoadmapItemType.BOOK.value == "BOOK"
    assert RoadmapItemType.CERTIFICATE.value == "CERTIFICATE"
    assert RoadmapItemType.INTERNSHIP.value == "INTERNSHIP"
    assert RoadmapItemType.BOOTCAMP.value == "BOOTCAMP"
    assert RoadmapItemType.CAREER.value == "CAREER"


def test_roadmap_hierarchical_structure(test_db_session, test_roadmap):
    """Test hierarchical roadmap structure with parent-child relationships."""
    from database.models import RoadmapItem

    items = test_db_session.query(RoadmapItem).filter(RoadmapItem.roadmap_id == test_roadmap.id).all()

    # Should have 3 items (root, child, leaf)
    assert len(items) == 3

    # Find root item
    root_item = next(item for item in items if item.parent_id is None)
    assert root_item.level == 0
    assert root_item.is_leaf is False

    # Find child item
    child_items = [item for item in items if item.parent_id == root_item.id]
    assert len(child_items) == 1
    child_item = child_items[0]
    assert child_item.level == 1
    assert child_item.parent_id == root_item.id

    # Find leaf item
    leaf_items = [item for item in items if item.parent_id == child_item.id]
    assert len(leaf_items) == 1
    leaf_item = leaf_items[0]
    assert leaf_item.level == 2
    assert leaf_item.is_leaf is True
    assert leaf_item.is_career_goal is True
    assert leaf_item.item_type == RoadmapItemType.CAREER


def test_topic_field_creation(test_db_session):
    """Test creating a topic field."""
    from database.models import TopicField

    topic_field = TopicField(
        name="Full Stack Development",
        description="Komplette Web-Entwicklung",
        system_prompt="You are an expert in Full Stack Development.",
    )
    test_db_session.add(topic_field)
    test_db_session.commit()

    assert topic_field.id is not None
    assert topic_field.name == "Full Stack Development"


def test_career_tree_node_relationship(test_db_session, test_study_program, test_topic_field):
    """Test CareerTreeNode -> TopicField relationship."""
    from database.models import CareerTreeNode

    node = CareerTreeNode(
        name="Full Stack Development",
        description="Full stack development career path",
        study_program_id=test_study_program.id,
        topic_field_id=test_topic_field.id,
        is_leaf=True,
        level=0,
    )
    test_db_session.add(node)
    test_db_session.commit()

    assert node.topic_field_id == test_topic_field.id
    test_db_session.refresh(node)
    assert node.topic_field is not None
    assert node.topic_field.id == test_topic_field.id


def test_cascade_delete_user_profile(test_db_session, test_user):
    """Test that deleting a user cascades to profile."""
    from database.models import UserProfile

    profile = UserProfile(
        user_id=test_user.id,
        current_semester=3,
    )
    test_db_session.add(profile)
    test_db_session.commit()

    profile_id = profile.id

    # Delete user
    test_db_session.delete(test_user)
    test_db_session.commit()

    # Profile should be deleted
    deleted_profile = test_db_session.query(UserProfile).filter(UserProfile.id == profile_id).first()
    assert deleted_profile is None

