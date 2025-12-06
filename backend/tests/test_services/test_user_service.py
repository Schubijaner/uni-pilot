"""Tests for User Service."""

import pytest
from datetime import datetime

from api.core.exceptions import NotFoundError
from api.models.user import UserProfileCreate
from api.services.user_service import UserService
from database.models import Module, UserModuleProgress, UserProfile


def test_get_or_create_profile_create(test_db_session, test_user, test_university, test_study_program):
    """Test creating a new profile."""
    profile_data = UserProfileCreate(
        university_id=test_university.id,
        study_program_id=test_study_program.id,
        current_semester=3,
        skills="Python, JavaScript",
    )

    profile = UserService.get_or_create_profile(
        user_id=test_user.id,
        profile_data=profile_data,
        db=test_db_session,
    )

    assert profile.id is not None
    assert profile.user_id == test_user.id
    assert profile.university_id == test_university.id
    assert profile.study_program_id == test_study_program.id
    assert profile.current_semester == 3
    assert profile.skills == "Python, JavaScript"


def test_get_or_create_profile_update(test_db_session, test_user, test_university, test_study_program):
    """Test updating an existing profile."""
    # Create initial profile
    profile_data1 = UserProfileCreate(
        university_id=test_university.id,
        study_program_id=test_study_program.id,
        current_semester=2,
        skills="Python",
    )
    profile1 = UserService.get_or_create_profile(
        user_id=test_user.id,
        profile_data=profile_data1,
        db=test_db_session,
    )
    profile_id = profile1.id

    # Update profile
    profile_data2 = UserProfileCreate(
        university_id=test_university.id,
        study_program_id=test_study_program.id,
        current_semester=4,
        skills="Python, JavaScript, SQL",
    )
    profile2 = UserService.get_or_create_profile(
        user_id=test_user.id,
        profile_data=profile_data2,
        db=test_db_session,
    )

    assert profile2.id == profile_id  # Same profile
    assert profile2.current_semester == 4
    assert profile2.skills == "Python, JavaScript, SQL"


def test_get_profile_not_found(test_db_session, test_user):
    """Test getting a non-existent profile."""
    profile = UserService.get_profile(test_user.id, test_db_session)
    assert profile is None


def test_get_profile_exists(test_db_session, test_user, test_university, test_study_program):
    """Test getting an existing profile."""
    profile_data = UserProfileCreate(
        university_id=test_university.id,
        study_program_id=test_study_program.id,
        current_semester=3,
    )
    created_profile = UserService.get_or_create_profile(
        user_id=test_user.id,
        profile_data=profile_data,
        db=test_db_session,
    )

    retrieved_profile = UserService.get_profile(test_user.id, test_db_session)
    assert retrieved_profile is not None
    assert retrieved_profile.id == created_profile.id


def test_get_user_modules(test_db_session, test_user, test_module):
    """Test getting user modules with progress."""
    # Create module progress
    progress = UserModuleProgress(
        user_id=test_user.id,
        module_id=test_module.id,
        completed=True,
        grade="1.7",
    )
    test_db_session.add(progress)
    test_db_session.commit()

    modules = UserService.get_user_modules(test_user.id, test_db_session)
    assert len(modules) == 1
    assert modules[0].module_id == test_module.id
    assert modules[0].completed is True
    assert modules[0].grade == "1.7"


def test_update_module_progress_create(test_db_session, test_user, test_module):
    """Test creating module progress."""
    progress = UserService.update_module_progress(
        user_id=test_user.id,
        module_id=test_module.id,
        completed=True,
        db=test_db_session,
        grade="2.0",
        completed_at=datetime.utcnow().isoformat(),
    )

    # UserModuleProgress has composite primary key (user_id, module_id), no separate id
    assert progress.user_id == test_user.id
    assert progress.module_id == test_module.id
    assert progress.completed is True
    assert progress.grade == "2.0"


def test_update_module_progress_update(test_db_session, test_user, test_module):
    """Test updating existing module progress."""
    # Create initial progress
    progress1 = UserService.update_module_progress(
        user_id=test_user.id,
        module_id=test_module.id,
        completed=False,
        db=test_db_session,
    )
    # Store composite key (UserModuleProgress has no separate id)
    original_user_id = progress1.user_id
    original_module_id = progress1.module_id

    # Update progress
    progress2 = UserService.update_module_progress(
        user_id=test_user.id,
        module_id=test_module.id,
        completed=True,
        db=test_db_session,
        grade="1.5",
    )

    # Verify it's the same record (same composite key)
    assert progress2.user_id == original_user_id
    assert progress2.module_id == original_module_id
    assert progress2.completed is True
    assert progress2.grade == "1.5"


def test_update_module_progress_module_not_found(test_db_session, test_user):
    """Test updating progress for non-existent module."""
    with pytest.raises(NotFoundError) as exc_info:
        UserService.update_module_progress(
            user_id=test_user.id,
            module_id=99999,  # Non-existent module
            completed=True,
            db=test_db_session,
        )

    assert "module" in exc_info.value.message.lower()


def test_get_roadmap_progress(test_db_session, test_user, test_topic_field, test_roadmap):
    """Test getting roadmap progress."""
    from database.models import RoadmapItem, UserProfile, UserRoadmapItem

    # Create profile with selected topic field
    profile = UserProfile(
        user_id=test_user.id,
        selected_topic_field_id=test_topic_field.id,
    )
    test_db_session.add(profile)
    test_db_session.commit()

    # Get roadmap items
    roadmap_items = test_db_session.query(RoadmapItem).filter(RoadmapItem.roadmap_id == test_roadmap.id).all()

    # Mark one item as completed
    completed_item = roadmap_items[0]
    user_progress = UserRoadmapItem(
        user_id=test_user.id,
        roadmap_item_id=completed_item.id,
        completed=True,
    )
    test_db_session.add(user_progress)
    test_db_session.commit()

    progress_data = UserService.get_roadmap_progress(
        user_id=test_user.id,
        topic_field_id=test_topic_field.id,
        db=test_db_session,
    )

    assert progress_data is not None
    assert "roadmap" in progress_data
    assert "items" in progress_data
    assert "progress_percentage" in progress_data
    assert progress_data["progress_percentage"] > 0
    # Fix: progress_map contains UserRoadmapItem objects, check properly
    progress_map = progress_data["user_progress"]
    assert completed_item.id in progress_map
    assert progress_map[completed_item.id].completed is True


def test_get_roadmap_progress_no_profile(test_db_session, test_user):
    """Test getting roadmap progress without profile."""
    with pytest.raises(NotFoundError):
        UserService.get_roadmap_progress(
            user_id=test_user.id,
            topic_field_id=None,
            db=test_db_session,
        )


def test_update_roadmap_item_progress_create(test_db_session, test_user, test_roadmap):
    """Test creating roadmap item progress."""
    from database.models import RoadmapItem

    roadmap_item = (
        test_db_session.query(RoadmapItem).filter(RoadmapItem.roadmap_id == test_roadmap.id).first()
    )

    progress = UserService.update_roadmap_item_progress(
        user_id=test_user.id,
        roadmap_item_id=roadmap_item.id,
        completed=True,
        db=test_db_session,
        completed_at=datetime.utcnow().isoformat(),
        notes="Great resource!",
    )

    # UserRoadmapItem has composite primary key (user_id, roadmap_item_id), no separate id
    assert progress.user_id == test_user.id
    assert progress.roadmap_item_id == roadmap_item.id
    assert progress.completed is True
    assert progress.notes == "Great resource!"


def test_update_roadmap_item_progress_not_found(test_db_session, test_user):
    """Test updating progress for non-existent roadmap item."""
    with pytest.raises(NotFoundError):
        UserService.update_roadmap_item_progress(
            user_id=test_user.id,
            roadmap_item_id=99999,  # Non-existent item
            completed=True,
            db=test_db_session,
        )

