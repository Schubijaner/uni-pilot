"""User profile and progress router."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.core.exceptions import NotFoundError
from api.dependencies import get_current_user, get_db
from api.models.user import (
    ModuleProgressUpdate,
    RoadmapProgressUpdate,
    UserModuleProgressResponse,
    UserProfileCreate,
    UserProfileResponse,
)
from api.services.user_service import UserService
from database.models import User

router = APIRouter(prefix="/api/v1/users/me", tags=["users"])


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's profile.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        User profile information

    Raises:
        HTTPException: If profile not found
    """
    profile = UserService.get_profile(current_user.id, db)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete onboarding first.",
        )
    return UserProfileResponse.model_validate(profile)


@router.put("/profile", response_model=UserProfileResponse)
async def create_or_update_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create or update user profile (onboarding).

    Args:
        profile_data: Profile data to create/update
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user profile
    """
    profile = UserService.get_or_create_profile(
        user_id=current_user.id,
        profile_data=profile_data,
        db=db,
    )
    return UserProfileResponse.model_validate(profile)


@router.get("/modules", response_model=List[UserModuleProgressResponse])
async def get_user_modules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all modules with progress for current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of user module progress
    """
    progress_list = UserService.get_user_modules(current_user.id, db)

    # Convert to response models
    result = []
    for progress in progress_list:
        result.append(
            UserModuleProgressResponse(
                module={
                    "id": progress.module.id,
                    "name": progress.module.name,
                    "description": progress.module.description,
                    "module_type": progress.module.module_type.value,
                    "semester": progress.module.semester,
                },
                completed=progress.completed,
                grade=progress.grade,
                completed_at=progress.completed_at,
            )
        )

    return result


@router.put("/modules/{module_id}/progress", response_model=UserModuleProgressResponse)
async def update_module_progress(
    module_id: int,
    progress_data: ModuleProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update or create module progress for current user.

    Args:
        module_id: Module ID
        progress_data: Progress update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated module progress

    Raises:
        HTTPException: If module not found
    """
    try:
        completed_at_str = (
            progress_data.completed_at.isoformat() if progress_data.completed_at else None
        )
        progress = UserService.update_module_progress(
            user_id=current_user.id,
            module_id=module_id,
            completed=progress_data.completed,
            db=db,
            grade=progress_data.grade,
            completed_at=completed_at_str,
        )

        return UserModuleProgressResponse(
            module={
                "id": progress.module.id,
                "name": progress.module.name,
                "description": progress.module.description,
                "module_type": progress.module.module_type.value,
                "semester": progress.module.semester,
            },
            completed=progress.completed,
            grade=progress.grade,
            completed_at=progress.completed_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/roadmap/progress")
async def get_roadmap_progress(
    topic_field_id: Optional[int] = Query(None, description="Optional topic field ID to filter by"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get roadmap progress for current user.

    Args:
        topic_field_id: Optional topic field ID to filter by
        current_user: Current authenticated user
        db: Database session

    Returns:
        Roadmap progress information

    Raises:
        HTTPException: If roadmap or profile not found
    """
    try:
        progress_data = UserService.get_roadmap_progress(
            user_id=current_user.id,
            topic_field_id=topic_field_id,
            db=db,
        )

        # Format response
        from api.models.roadmap import RoadmapItemResponse

        items_response = []
        for item in progress_data["items"]:
            progress_item = progress_data["user_progress"].get(item.id)
            items_response.append(
                {
                    "item": RoadmapItemResponse.model_validate(item),
                    "completed": progress_item.completed if progress_item else False,
                    "completed_at": progress_item.completed_at if progress_item else None,
                    "notes": progress_item.notes if progress_item else None,
                }
            )

        return {
            "roadmap": progress_data["roadmap"],
            "items": items_response,
            "progress_percentage": progress_data["progress_percentage"],
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/roadmap/items/{roadmap_item_id}/progress")
async def update_roadmap_item_progress(
    roadmap_item_id: int,
    progress_data: RoadmapProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update or create roadmap item progress for current user.

    Args:
        roadmap_item_id: Roadmap item ID
        progress_data: Progress update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated roadmap item progress

    Raises:
        HTTPException: If roadmap item not found
    """
    try:
        completed_at_str = (
            progress_data.completed_at.isoformat() if progress_data.completed_at else None
        )
        progress = UserService.update_roadmap_item_progress(
            user_id=current_user.id,
            roadmap_item_id=roadmap_item_id,
            completed=progress_data.completed,
            db=db,
            completed_at=completed_at_str,
            notes=progress_data.notes,
        )

        return {
            "roadmap_item_id": progress.roadmap_item_id,
            "completed": progress.completed,
            "completed_at": progress.completed_at,
            "notes": progress.notes,
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

