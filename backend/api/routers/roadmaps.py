"""Roadmaps router."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session

from api.core.exceptions import LLMError, NotFoundError
from api.dependencies import get_current_user, get_db
from api.models.roadmap import RoadmapGenerateRequest, RoadmapResponse
from api.services.roadmap_service import RoadmapService
from api.services.user_service import UserService
from database.models import StudyProgram, TopicField, User

router = APIRouter(prefix="/api/v1/topic-fields", tags=["roadmaps"])


@router.get("/{topic_field_id}/roadmap", response_model=RoadmapResponse)
async def get_roadmap(
    topic_field_id: int,
    format: str = Query("tree", description="Format: 'tree' (hierarchisch) or 'flat' (flat list)"),
    db: Session = Depends(get_db),
):
    """
    Get roadmap for a topic field.

    Args:
        topic_field_id: Topic field ID
        format: Response format ('tree' or 'flat')
        db: Database session

    Returns:
        Roadmap with hierarchical tree structure

    Raises:
        HTTPException: If roadmap not found
    """
    try:
        roadmap_response = RoadmapService.get_roadmap_with_tree(topic_field_id, db)

        if not roadmap_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roadmap for topic field {topic_field_id} not found. Generate it first.",
            )

        # If format is 'flat', we still return the full response (items are flat, tree is optional)
        # Frontend can choose which to use
        return roadmap_response
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting roadmap for topic_field_id {topic_field_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/{topic_field_id}/roadmap/generate", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
async def generate_roadmap(
    topic_field_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a new roadmap for a topic field using LLM.

    Args:
        topic_field_id: Topic field ID
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session

    Returns:
        Generated roadmap

    Raises:
        HTTPException: If topic field, user profile, or study program not found, or LLM generation fails
    """
    # Verify topic field exists
    topic_field = db.query(TopicField).filter(TopicField.id == topic_field_id).first()
    if not topic_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic field with id {topic_field_id} not found",
        )

    # Get user profile
    profile = UserService.get_profile(current_user.id, db)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete onboarding first.",
        )

    if not profile.study_program_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile missing study program. Please complete onboarding first.",
        )

    # Get study program
    study_program = db.query(StudyProgram).filter(StudyProgram.id == profile.study_program_id).first()
    if not study_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study program with id {profile.study_program_id} not found",
        )

    # Check if roadmap already exists
    existing_roadmap = RoadmapService.get_roadmap(topic_field_id, db)
    if existing_roadmap:
        # Return existing roadmap
        roadmap_response = RoadmapService.get_roadmap_with_tree(topic_field_id, db)
        return roadmap_response

    # Generate roadmap
    try:
        roadmap_service = RoadmapService()
        roadmap = roadmap_service.generate_roadmap(
            user_profile=profile,
            topic_field=topic_field,
            study_program=study_program,
            db=db,
        )

        # Return roadmap with tree structure
        roadmap_response = RoadmapService.get_roadmap_with_tree(topic_field_id, db)
        return roadmap_response
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate roadmap: {e.message}",
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

