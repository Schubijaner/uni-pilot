"""Modules router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models.user import ModuleResponse, PaginatedModulesResponse
from database.models import Module, ModuleType, StudyProgram

router = APIRouter(prefix="/api/v1/study-programs", tags=["modules"])


@router.get("/{study_program_id}/modules", response_model=PaginatedModulesResponse)
async def get_modules_by_study_program(
    study_program_id: int,
    module_type: Optional[str] = Query(None, description="Filter by module type (REQUIRED or ELECTIVE)"),
    semester: Optional[int] = Query(None, description="Filter by recommended semester"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Get all modules for a study program.

    Args:
        study_program_id: Study program ID
        module_type: Optional filter by module type
        semester: Optional filter by semester
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session

    Returns:
        Paginated list of modules

    Raises:
        HTTPException: If study program not found
    """
    # Verify study program exists
    study_program = db.query(StudyProgram).filter(StudyProgram.id == study_program_id).first()
    if not study_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study program with id {study_program_id} not found",
        )

    query = db.query(Module).filter(Module.study_program_id == study_program_id)

    if module_type:
        try:
            module_type_enum = ModuleType(module_type)
            query = query.filter(Module.module_type == module_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid module_type: {module_type}. Must be 'REQUIRED' or 'ELECTIVE'",
            )

    if semester is not None:
        query = query.filter(Module.semester == semester)

    total = query.count()
    modules = query.offset(offset).limit(limit).all()

    return PaginatedModulesResponse(
        items=[ModuleResponse.model_validate(m) for m in modules],
        total=total,
        limit=limit,
        offset=offset,
    )

