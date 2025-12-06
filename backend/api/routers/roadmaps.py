"""Roadmaps router."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session

from api.core.exceptions import LLMError, NotFoundError
from api.dependencies import get_current_user, get_db
from api.models.roadmap import RoadmapGenerateRequest, RoadmapResponse
from api.services.career_service import CareerService
from api.services.roadmap_service import RoadmapService
from api.services.user_service import UserService
from database.models import CareerTreeNode, StudyProgram, TopicField, User

logger = logging.getLogger(__name__)
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


@router.post("/jobs/{job_id}/roadmap/generate", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
async def generate_roadmap_for_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a new roadmap for a specific job using LLM.

    Args:
        job_id: Career tree node ID (must be a leaf node)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Generated roadmap

    Raises:
        HTTPException: If job not found, not a leaf node, user profile or study program not found, or LLM generation fails
    """
    try:
        # Verify job exists and is a leaf node
        job = CareerService.get_job(job_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

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

    # Generate roadmap for job
    try:
        roadmap_service = RoadmapService()
        roadmap = roadmap_service.generate_roadmap_for_job(
            user_profile=profile,
            job=job,
            study_program=study_program,
            db=db,
        )

        # Return roadmap with tree structure
        # Note: We need to get the topic_field_id from the roadmap to return it properly
        roadmap_response = RoadmapService.get_roadmap_with_tree(roadmap.topic_field_id, db)
        return roadmap_response
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate roadmap: {e.message}",
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

