"""User service for profile and progress management."""

from typing import List, Optional

from sqlalchemy.orm import Session

from api.core.exceptions import NotFoundError
from api.models.user import UserProfileCreate
from database.models import (
    Module,
    RoadmapItem,
    StudyProgram,
    User,
    UserModuleProgress,
    UserProfile,
    UserRoadmapItem,
)

# Remove unused import if not needed


class UserService:
    """Service for user profile and progress operations."""

    @staticmethod
    def get_or_create_profile(
        user_id: int,
        profile_data: UserProfileCreate,
        db: Session,
    ) -> UserProfile:
        """
        Get or create user profile.

        Args:
            user_id: User ID
            profile_data: Profile data to create/update
            db: Database session

        Returns:
            UserProfile object
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if not profile:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                university_id=profile_data.university_id,
                study_program_id=profile_data.study_program_id,
                current_semester=profile_data.current_semester,
                skills=profile_data.skills,
            )
            db.add(profile)
        else:
            # Update existing profile
            if profile_data.university_id is not None:
                profile.university_id = profile_data.university_id
            if profile_data.study_program_id is not None:
                profile.study_program_id = profile_data.study_program_id
            if profile_data.current_semester is not None:
                profile.current_semester = profile_data.current_semester
            if profile_data.skills is not None:
                profile.skills = profile_data.skills

        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get_profile(user_id: int, db: Session) -> Optional[UserProfile]:
        """
        Get user profile.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            UserProfile or None if not found
        """
        return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    @staticmethod
    def get_user_modules(user_id: int, db: Session) -> List[UserModuleProgress]:
        """
        Get all modules with progress for a user.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            List of UserModuleProgress objects
        """
        return db.query(UserModuleProgress).filter(UserModuleProgress.user_id == user_id).all()

    @staticmethod
    def update_module_progress(
        user_id: int,
        module_id: int,
        completed: bool,
        db: Session,
        grade: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> UserModuleProgress:
        """
        Update or create module progress for user.

        Args:
            user_id: User ID
            module_id: Module ID
            completed: Whether module is completed
            grade: Optional grade
            completed_at: Optional completion date (ISO format string)
            db: Database session

        Returns:
            UserModuleProgress object

        Raises:
            NotFoundError: If module not found
        """
        # Verify module exists
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise NotFoundError(f"Module with id {module_id} not found", "MODULE_NOT_FOUND")

        # Get or create progress
        progress = (
            db.query(UserModuleProgress)
            .filter(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.module_id == module_id,
            )
            .first()
        )

        if not progress:
            progress = UserModuleProgress(
                user_id=user_id,
                module_id=module_id,
                completed=completed,
                grade=grade,
            )
            db.add(progress)
            db.flush()  # Flush to get the ID
            db.refresh(progress)  # Refresh to populate the ID
        else:
            progress.completed = completed
            if grade is not None:
                progress.grade = grade

        if completed_at:
            from datetime import datetime

            progress.completed_at = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))

        db.commit()
        db.refresh(progress)  # Final refresh after commit
        return progress

    @staticmethod
    def get_roadmap_progress(user_id: int, topic_field_id: Optional[int], db: Session) -> dict:
        """
        Get roadmap progress for user.

        Args:
            user_id: User ID
            topic_field_id: Optional topic field ID to filter by
            db: Database session

        Returns:
            Dictionary with roadmap progress information
        """
        from database.models import Roadmap, TopicField

        # Get user profile
        profile = UserService.get_profile(user_id, db)
        if not profile or not profile.selected_topic_field_id:
            raise NotFoundError("User has no selected topic field", "NO_TOPIC_FIELD")

        # Use provided topic_field_id or user's selected one
        target_topic_field_id = topic_field_id or profile.selected_topic_field_id

        # Get roadmap
        roadmap = (
            db.query(Roadmap).filter(Roadmap.topic_field_id == target_topic_field_id).first()
        )
        if not roadmap:
            raise NotFoundError(
                f"Roadmap for topic field {target_topic_field_id} not found",
                "ROADMAP_NOT_FOUND",
            )

        # Get all roadmap items
        roadmap_items = (
            db.query(RoadmapItem).filter(RoadmapItem.roadmap_id == roadmap.id).all()
        )

        # Get user progress for all items
        item_ids = [item.id for item in roadmap_items]
        user_progress = (
            db.query(UserRoadmapItem)
            .filter(
                UserRoadmapItem.user_id == user_id,
                UserRoadmapItem.roadmap_item_id.in_(item_ids),
            )
            .all()
        )

        # Create progress map with UserRoadmapItem objects (not dicts)
        progress_map = {p.roadmap_item_id: p for p in user_progress}

        # Calculate progress
        total_items = len(roadmap_items)
        completed_items = sum(1 for item_id in item_ids if progress_map.get(item_id) and progress_map.get(item_id).completed)
        progress_percentage = (completed_items / total_items * 100) if total_items > 0 else 0.0

        return {
            "roadmap": {"id": roadmap.id, "topic_field_id": roadmap.topic_field_id, "name": roadmap.name},
            "items": roadmap_items,
            "user_progress": progress_map,
            "progress_percentage": progress_percentage,
        }

    @staticmethod
    def update_roadmap_item_progress(
        user_id: int,
        roadmap_item_id: int,
        completed: bool,
        db: Session,
        completed_at: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> UserRoadmapItem:
        """
        Update or create roadmap item progress for user.

        Args:
            user_id: User ID
            roadmap_item_id: Roadmap item ID
            completed: Whether item is completed
            completed_at: Optional completion date (ISO format string)
            notes: Optional notes
            db: Database session

        Returns:
            UserRoadmapItem object

        Raises:
            NotFoundError: If roadmap item not found
        """
        # Verify roadmap item exists
        roadmap_item = db.query(RoadmapItem).filter(RoadmapItem.id == roadmap_item_id).first()
        if not roadmap_item:
            raise NotFoundError(
                f"Roadmap item with id {roadmap_item_id} not found",
                "ROADMAP_ITEM_NOT_FOUND",
            )

        # Get or create progress
        progress = (
            db.query(UserRoadmapItem)
            .filter(
                UserRoadmapItem.user_id == user_id,
                UserRoadmapItem.roadmap_item_id == roadmap_item_id,
            )
            .first()
        )

        if not progress:
            progress = UserRoadmapItem(
                user_id=user_id,
                roadmap_item_id=roadmap_item_id,
                completed=completed,
            )
            db.add(progress)
            db.flush()  # Flush to get the ID
            db.refresh(progress)  # Refresh to populate the ID
        else:
            progress.completed = completed

        if completed_at:
            from datetime import datetime

            progress.completed_at = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))

        if notes is not None:
            progress.notes = notes

        db.commit()
        db.refresh(progress)  # Final refresh after commit
        return progress

