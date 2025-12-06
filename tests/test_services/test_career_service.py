"""Tests for Career Service."""

import pytest

from api.core.exceptions import NotFoundError
from api.services.career_service import CareerService
from database.models import CareerTreeRelationship, CareerTreeNode, TopicField, UserProfile


def test_get_career_tree_hierarchical(test_db_session, test_study_program):
    """Test getting career tree with hierarchical structure."""
    from database.models import TopicField

    # Create topic fields
    topic1 = TopicField(name="Frontend", description="Frontend development")
    topic2 = TopicField(name="Backend", description="Backend development")
    test_db_session.add_all([topic1, topic2])
    test_db_session.flush()

    # Create hierarchical career tree nodes
    root_node = CareerTreeNode(
        name="Software Development",
        description="Root node",
        study_program_id=test_study_program.id,
        is_leaf=False,
        level=0,
    )
    test_db_session.add(root_node)
    test_db_session.flush()

    frontend_node = CareerTreeNode(
        name="Frontend Developer",
        description="Frontend career",
        study_program_id=test_study_program.id,
        topic_field_id=topic1.id,
        is_leaf=True,
        level=1,
    )
    backend_node = CareerTreeNode(
        name="Backend Developer",
        description="Backend career",
        study_program_id=test_study_program.id,
        topic_field_id=topic2.id,
        is_leaf=True,
        level=1,
    )
    test_db_session.add_all([frontend_node, backend_node])
    test_db_session.flush()

    # Create relationships
    rel1 = CareerTreeRelationship(parent_id=root_node.id, child_id=frontend_node.id)
    rel2 = CareerTreeRelationship(parent_id=root_node.id, child_id=backend_node.id)
    test_db_session.add_all([rel1, rel2])
    test_db_session.commit()

    # Get career tree
    tree_response = CareerService.get_career_tree(test_study_program.id, test_db_session)

    assert tree_response.study_program_id == test_study_program.id
    assert tree_response.nodes is not None
    assert tree_response.nodes.id == root_node.id
    assert len(tree_response.nodes.children) == 2


def test_get_career_tree_empty(test_db_session, test_study_program):
    """Test getting career tree for study program with no nodes."""
    tree_response = CareerService.get_career_tree(test_study_program.id, test_db_session)

    assert tree_response.study_program_id == test_study_program.id
    assert tree_response.nodes is None


def test_get_topic_field(test_db_session, test_topic_field):
    """Test getting topic field by ID."""
    topic_field = CareerService.get_topic_field(test_topic_field.id, test_db_session)

    assert topic_field.id == test_topic_field.id
    assert topic_field.name == test_topic_field.name


def test_get_topic_field_not_found(test_db_session):
    """Test getting non-existent topic field."""
    with pytest.raises(NotFoundError):
        CareerService.get_topic_field(99999, test_db_session)


def test_select_topic_field(test_db_session, test_user, test_topic_field):
    """Test selecting topic field for user."""
    # Create profile first
    profile = UserProfile(
        user_id=test_user.id,
        current_semester=3,
    )
    test_db_session.add(profile)
    test_db_session.commit()

    updated_profile = CareerService.select_topic_field(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )

    assert updated_profile.selected_topic_field_id == test_topic_field.id


def test_select_topic_field_no_profile(test_db_session, test_user, test_topic_field):
    """Test selecting topic field without profile."""
    with pytest.raises(NotFoundError) as exc_info:
        CareerService.select_topic_field(
            user_id=test_user.id,
            topic_field_id=test_topic_field.id,
            db=test_db_session,
        )

    assert "profile" in exc_info.value.message.lower()


def test_create_user_question(test_db_session, test_user, test_career_tree_node):
    """Test creating user question."""
    from database.models import UserQuestion

    user_question = CareerService.create_user_question(
        user_id=test_user.id,
        question_text="Are you interested in frontend development?",
        answer=True,
        db=test_db_session,
        career_tree_node_id=test_career_tree_node.id,
    )

    assert user_question.id is not None
    assert user_question.user_id == test_user.id
    assert user_question.question_text == "Are you interested in frontend development?"
    assert user_question.answer is True
    assert user_question.career_tree_node_id == test_career_tree_node.id


def test_create_user_question_without_node(test_db_session, test_user):
    """Test creating user question without career tree node."""
    from database.models import UserQuestion

    user_question = CareerService.create_user_question(
        user_id=test_user.id,
        question_text="General question?",
        answer=False,
        db=test_db_session,
        career_tree_node_id=None,
    )

    assert user_question.id is not None
    assert user_question.career_tree_node_id is None

