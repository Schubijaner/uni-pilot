"""Onboarding router (universities, study programs, career tree, topic fields)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.core.exceptions import NotFoundError
from api.dependencies import get_current_user, get_db
from api.models.career import CareerTreeResponse, TopicFieldResponse, TopicFieldSelectRequest, UserQuestionCreate
from api.models.user import PaginatedStudyProgramsResponse, PaginatedUniversitiesResponse, StudyProgramResponse, UniversityResponse, UserProfileResponse
from api.services.career_service import CareerService
from api.services.user_service import UserService
from database.models import StudyProgram, University, User

router = APIRouter(prefix="/api/v1", tags=["onboarding"])


@router.get("/universities", response_model=PaginatedUniversitiesResponse)
async def get_universities(
    search: Optional[str] = Query(None, description="Search term for name or abbreviation"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Get all available universities.

    Args:
        search: Optional search term
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session

    Returns:
        Paginated list of universities
    """
    query = db.query(University)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (University.name.ilike(search_term)) | (University.abbreviation.ilike(search_term))
        )

    total = query.count()
    universities = query.offset(offset).limit(limit).all()

    return PaginatedUniversitiesResponse(
        items=[UniversityResponse.model_validate(u) for u in universities],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/universities/{university_id}/study-programs", response_model=PaginatedStudyProgramsResponse)
async def get_study_programs_by_university(
    university_id: int,
    degree_type: Optional[str] = Query(None, description="Filter by degree type"),
    db: Session = Depends(get_db),
):
    """
    Get all study programs for a university.

    Args:
        university_id: University ID
        degree_type: Optional filter by degree type
        db: Database session

    Returns:
        List of study programs

    Raises:
        HTTPException: If university not found
    """
    university = db.query(University).filter(University.id == university_id).first()
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"University with id {university_id} not found",
        )

    query = db.query(StudyProgram).filter(StudyProgram.university_id == university_id)

    if degree_type:
        query = query.filter(StudyProgram.degree_type == degree_type)

    study_programs = query.all()

    return PaginatedStudyProgramsResponse(
        items=[StudyProgramResponse.model_validate(sp) for sp in study_programs],
        total=len(study_programs),
    )


@router.get("/study-programs/{study_program_id}/career-tree", response_model=CareerTreeResponse)
async def get_career_tree(
    study_program_id: int,
    db: Session = Depends(get_db),
):
    """
    Get career tree (Themenfelder-Tree) for a study program.

    Args:
        study_program_id: Study program ID
        db: Database session

    Returns:
        Hierarchical career tree structure

    Raises:
        HTTPException: If study program not found
    """
    study_program = db.query(StudyProgram).filter(StudyProgram.id == study_program_id).first()
    if not study_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study program with id {study_program_id} not found",
        )

    tree = CareerService.get_career_tree(study_program_id, db)
    return tree


@router.get("/topic-fields", response_model=List[TopicFieldBase])
async def get_topic_fields(
    search: Optional[str] = Query(None, description="Search term"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Get all available topic fields.

    Args:
        search: Optional search term
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session

    Returns:
        List of topic fields
    """
    from database.models import TopicField

    query = db.query(TopicField)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (TopicField.name.ilike(search_term)) | (TopicField.description.ilike(search_term))
        )

    topic_fields = query.offset(offset).limit(limit).all()

    return [TopicFieldResponse.model_validate(tf) for tf in topic_fields]


@router.get("/topic-fields/{topic_field_id}", response_model=TopicFieldBase)
async def get_topic_field(
    topic_field_id: int,
    db: Session = Depends(get_db),
):
    """
    Get topic field by ID.

    Args:
        topic_field_id: Topic field ID
        db: Database session

    Returns:
        Topic field details

    Raises:
        HTTPException: If topic field not found
    """
    try:
        topic_field = CareerService.get_topic_field(topic_field_id, db)
        return TopicFieldResponse.model_validate(topic_field)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put("/users/me/profile/topic-field", response_model=UserProfileResponse)
async def select_topic_field(
    request: TopicFieldSelectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Select topic field for current user (after career tree navigation).

    Args:
        request: Topic field selection request
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user profile

    Raises:
        HTTPException: If topic field not found or profile not found
    """
    try:
        profile = CareerService.select_topic_field(
            user_id=current_user.id,
            topic_field_id=request.topic_field_id,
            db=db,
        )
        return UserProfileResponse.model_validate(profile)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/users/me/questions")
async def create_user_question(
    request: UserQuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create user question (for dynamic career tree adaptation).

    Args:
        question_text: Question text
        answer: User's answer (boolean)
        career_tree_node_id: Optional career tree node ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created user question
    """
    from api.models.user import UserQuestionResponse
    from database.models import UserQuestion

    user_question = CareerService.create_user_question(
        user_id=current_user.id,
        question_text=request.question_text,
        answer=request.answer,
        db=db,
        career_tree_node_id=request.career_tree_node_id,
    )

    return UserQuestionResponse.model_validate(user_question)


@router.get("/users/me/questions")
async def get_user_questions(
    career_tree_node_id: Optional[int] = Query(None, description="Filter by career tree node"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all user questions.

    Args:
        career_tree_node_id: Optional filter by career tree node
        limit: Maximum number of results
        offset: Pagination offset
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of user questions
    """
    from api.models.user import PaginatedUserQuestionsResponse, UserQuestionResponse
    from database.models import UserQuestion

    query = db.query(UserQuestion).filter(UserQuestion.user_id == current_user.id)

    if career_tree_node_id:
        query = query.filter(UserQuestion.career_tree_node_id == career_tree_node_id)

    total = query.count()
    questions = query.order_by(UserQuestion.created_at.desc()).offset(offset).limit(limit).all()

    return PaginatedUserQuestionsResponse(
        items=[UserQuestionResponse.model_validate(q) for q in questions],
        total=total,
        limit=limit,
        offset=offset,
    )

