"""Tests for database queries and query logic."""

import pytest

from database.models import CareerTreeRelationship, ModuleType, RoadmapItem, RoadmapItemType


def test_query_with_filtering(test_db_session, test_study_program):
    """Test querying with filters."""
    from database.models import Module

    # Create multiple modules
    module1 = Module(
        study_program_id=test_study_program.id,
        name="Module 1",
        module_type=ModuleType.REQUIRED,
        semester=1,
    )
    module2 = Module(
        study_program_id=test_study_program.id,
        name="Module 2",
        module_type=ModuleType.ELECTIVE,
        semester=2,
    )
    module3 = Module(
        study_program_id=test_study_program.id,
        name="Module 3",
        module_type=ModuleType.REQUIRED,
        semester=2,
    )
    test_db_session.add_all([module1, module2, module3])
    test_db_session.commit()

    # Filter by module type
    required_modules = test_db_session.query(Module).filter(Module.module_type == ModuleType.REQUIRED).all()
    assert len(required_modules) == 2

    # Filter by semester
    semester2_modules = test_db_session.query(Module).filter(Module.semester == 2).all()
    assert len(semester2_modules) == 2

    # Combined filter
    required_semester2 = (
        test_db_session.query(Module)
        .filter(Module.module_type == ModuleType.REQUIRED, Module.semester == 2)
        .all()
    )
    assert len(required_semester2) == 1
    assert required_semester2[0].name == "Module 3"


def test_query_pagination(test_db_session, test_study_program):
    """Test query pagination."""
    from database.models import Module

    # Create 10 modules
    modules = []
    for i in range(10):
        module = Module(
            study_program_id=test_study_program.id,
            name=f"Module {i}",
            module_type=ModuleType.REQUIRED,
            semester=1,
        )
        modules.append(module)
    test_db_session.add_all(modules)
    test_db_session.commit()

    # Test pagination
    limit = 3
    offset = 0

    page1 = test_db_session.query(Module).offset(offset).limit(limit).all()
    assert len(page1) == 3

    offset = 3
    page2 = test_db_session.query(Module).offset(offset).limit(limit).all()
    assert len(page2) == 3
    assert page1[0].id != page2[0].id


def test_hierarchical_roadmap_query(test_db_session, test_roadmap):
    """Test querying hierarchical roadmap structure."""
    items = test_db_session.query(RoadmapItem).filter(RoadmapItem.roadmap_id == test_roadmap.id).all()

    # Get root items
    root_items = [item for item in items if item.parent_id is None]
    assert len(root_items) == 1

    root_item = root_items[0]

    # Get children of root
    children = test_db_session.query(RoadmapItem).filter(RoadmapItem.parent_id == root_item.id).all()
    assert len(children) == 1

    # Get grandchildren (leaf nodes)
    leaf_items = test_db_session.query(RoadmapItem).filter(RoadmapItem.parent_id == children[0].id).all()
    assert len(leaf_items) == 1
    assert leaf_items[0].is_leaf is True


def test_career_tree_hierarchical_query(test_db_session, test_study_program):
    """Test querying hierarchical career tree structure."""
    from database.models import CareerTreeNode, TopicField

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

    # Query relationships
    relationships = (
        test_db_session.query(CareerTreeRelationship).filter(CareerTreeRelationship.parent_id == root_node.id).all()
    )
    assert len(relationships) == 2

    # Get child nodes
    child_ids = [rel.child_id for rel in relationships]
    children = test_db_session.query(CareerTreeNode).filter(CareerTreeNode.id.in_(child_ids)).all()
    assert len(children) == 2


def test_cascade_delete_roadmap_items(test_db_session, test_roadmap):
    """Test that deleting roadmap cascades to items."""
    item_ids = []
    items = test_db_session.query(RoadmapItem).filter(RoadmapItem.roadmap_id == test_roadmap.id).all()
    for item in items:
        item_ids.append(item.id)

    # Delete roadmap
    test_db_session.delete(test_roadmap)
    test_db_session.commit()

    # All items should be deleted
    for item_id in item_ids:
        deleted_item = test_db_session.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
        assert deleted_item is None


def test_query_with_join(test_db_session, test_user, test_university, test_study_program):
    """Test querying with joins."""
    from database.models import StudyProgram, University, UserProfile

    profile = UserProfile(
        user_id=test_user.id,
        university_id=test_university.id,
        study_program_id=test_study_program.id,
        current_semester=3,
    )
    test_db_session.add(profile)
    test_db_session.commit()

    # Query with join
    result = (
        test_db_session.query(UserProfile)
        .join(University)
        .join(StudyProgram)
        .filter(UserProfile.user_id == test_user.id)
        .first()
    )

    assert result is not None
    assert result.university_id == test_university.id
    assert result.study_program_id == test_study_program.id


def test_query_roadmap_items_by_level(test_db_session, test_roadmap):
    """Test querying roadmap items by level."""
    # Query items by level
    level_0_items = test_db_session.query(RoadmapItem).filter(
        RoadmapItem.roadmap_id == test_roadmap.id, RoadmapItem.level == 0
    ).all()
    assert len(level_0_items) == 1

    level_1_items = test_db_session.query(RoadmapItem).filter(
        RoadmapItem.roadmap_id == test_roadmap.id, RoadmapItem.level == 1
    ).all()
    assert len(level_1_items) == 1

    level_2_items = test_db_session.query(RoadmapItem).filter(
        RoadmapItem.roadmap_id == test_roadmap.id, RoadmapItem.level == 2
    ).all()
    assert len(level_2_items) == 1


def test_query_career_goals(test_db_session, test_roadmap):
    """Test querying career goal items."""
    career_goals = test_db_session.query(RoadmapItem).filter(
        RoadmapItem.roadmap_id == test_roadmap.id,
        RoadmapItem.is_career_goal == True,
        RoadmapItem.is_leaf == True,
    ).all()

    assert len(career_goals) == 1
    assert career_goals[0].item_type == RoadmapItemType.CAREER
    assert career_goals[0].is_leaf is True

