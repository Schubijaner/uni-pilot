"""Tests for Roadmap Service (without LLM)."""

import pytest

from api.services.roadmap_service import RoadmapService
from database.models import RoadmapItem, RoadmapItemType


def test_get_roadmap_with_tree(test_db_session, test_roadmap):
    """Test getting roadmap with hierarchical tree structure."""
    roadmap_response = RoadmapService.get_roadmap_with_tree(
        test_roadmap.topic_field_id, test_db_session
    )

    assert roadmap_response is not None
    assert roadmap_response.id == test_roadmap.id
    assert len(roadmap_response.items) == 3  # Root, child, leaf
    assert roadmap_response.tree is not None
    assert roadmap_response.tree.id is not None
    assert len(roadmap_response.tree.children) == 1  # One child


def test_get_roadmap_not_found(test_db_session):
    """Test getting non-existent roadmap."""
    roadmap_response = RoadmapService.get_roadmap_with_tree(99999, test_db_session)
    assert roadmap_response is None


def test_build_tree_from_items(test_db_session, test_roadmap):
    """Test building hierarchical tree structure from flat list."""
    from database.models import RoadmapItem

    items = test_db_session.query(RoadmapItem).filter(RoadmapItem.roadmap_id == test_roadmap.id).all()

    tree_root = RoadmapService.build_tree_from_items(items)

    assert tree_root is not None
    assert tree_root.parent_id is None
    assert tree_root.level == 0
    assert len(tree_root.children) == 1

    child = tree_root.children[0]
    assert child.parent_id == tree_root.id
    assert child.level == 1
    assert len(child.children) == 1

    leaf = child.children[0]
    assert leaf.parent_id == child.id
    assert leaf.level == 2
    assert leaf.is_leaf is True
    assert leaf.is_career_goal is True
    assert leaf.item_type == RoadmapItemType.CAREER


def test_build_tree_from_items_empty(test_db_session):
    """Test building tree from empty list."""
    tree_root = RoadmapService.build_tree_from_items([])
    assert tree_root is None


def test_get_roadmap(test_db_session, test_roadmap):
    """Test getting roadmap by topic field ID."""
    roadmap = RoadmapService.get_roadmap(test_roadmap.topic_field_id, test_db_session)

    assert roadmap is not None
    assert roadmap.id == test_roadmap.id
    assert roadmap.topic_field_id == test_roadmap.topic_field_id


def test_get_roadmap_not_found_by_field(test_db_session):
    """Test getting roadmap for non-existent topic field."""
    roadmap = RoadmapService.get_roadmap(99999, test_db_session)
    assert roadmap is None

