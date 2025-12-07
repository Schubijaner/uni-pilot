"""Roadmaps router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.exceptions import LLMError, NotFoundError
from api.dependencies import get_current_user, get_db
from api.models.roadmap import RoadmapResponse
from api.services.career_service import CareerService
from api.services.roadmap_service import RoadmapService
from api.services.user_service import UserService
from database.models import StudyProgram, TopicField, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/topic-fields", tags=["roadmaps"])


@router.post("/{topic_field_id}/roadmap", response_model=RoadmapResponse)
async def get_or_generate_roadmap(
    topic_field_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get existing roadmap for a topic field, or generate a new one if it doesn't exist.

    Args:
        topic_field_id: Topic field ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Existing or newly generated roadmap with hierarchical tree structure

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

    # Check if roadmap already exists - if yes, return it
    existing_roadmap = RoadmapService.get_roadmap(topic_field_id, db)
    if existing_roadmap:
        logger.info(f"Roadmap for topic field {topic_field_id} already exists. Returning existing.")
        roadmap_response = RoadmapService.get_roadmap_with_tree(topic_field_id, db)
        return roadmap_response

    # Roadmap doesn't exist - generate it
    logger.info(f"Roadmap for topic field {topic_field_id} not found. Generating new one.")

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


@router.post("/jobs/{job_id}/roadmap", response_model=RoadmapResponse)
async def get_or_generate_roadmap_for_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get existing roadmap for a specific job, or generate a new one if it doesn't exist.
    
    This endpoint validates the job, gets its topic_field_id, and then delegates
    to the topic_field roadmap endpoint. This is a convenience endpoint for jobs.

    Args:
        job_id: Career tree node ID (must be a leaf node)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Existing or newly generated roadmap with hierarchical tree structure

    Raises:
        HTTPException: If job not found, not a leaf node, or roadmap generation fails
    """
    try:
        # Verify job exists and is a leaf node
        job = CareerService.get_job(job_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)

    # Check if job has a topic_field_id
    if not job.topic_field_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} does not have a topic_field_id. Cannot retrieve or generate roadmap.",
        )

    # Delegate to the topic_field endpoint - it will handle get or generate logic
    # Since job.topic_field_id exists and is linked to the job, this will work correctly
    return await get_or_generate_roadmap(
        topic_field_id=job.topic_field_id,
        current_user=current_user,
        db=db,
    )

