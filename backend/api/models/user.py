"""User and profile-related Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UserProfileCreate(BaseModel):
    """User profile creation/update request."""

    university_id: Optional[int] = None
    study_program_id: Optional[int] = None
    current_semester: Optional[int] = None
    skills: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "university_id": 1,
                "study_program_id": 1,
                "current_semester": 3,
                "skills": "Python, JavaScript, SQL",
            }
        }


class UniversityResponse(BaseModel):
    """University response model."""

    id: int
    name: str
    abbreviation: Optional[str] = None

    class Config:
        from_attributes = True


class StudyProgramResponse(BaseModel):
    """Study program response model."""

    id: int
    name: str
    degree_type: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """User profile response model."""

    id: int
    user_id: int
    university_id: Optional[int] = None
    study_program_id: Optional[int] = None
    current_semester: Optional[int] = None
    skills: Optional[str] = None
    selected_topic_field_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    university: Optional[UniversityResponse] = None
    study_program: Optional[StudyProgramResponse] = None

    class Config:
        from_attributes = True


class ModuleProgressUpdate(BaseModel):
    """Module progress update request."""

    completed: bool
    grade: Optional[str] = None
    completed_at: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "completed": True,
                "grade": "1.7",
                "completed_at": "2024-01-10T00:00:00Z",
            }
        }


class ModuleResponse(BaseModel):
    """Module response model."""

    id: int
    name: str
    description: Optional[str] = None
    module_type: str
    semester: Optional[int] = None

    class Config:
        from_attributes = True


class UserModuleProgressResponse(BaseModel):
    """User module progress response."""

    module: ModuleResponse
    completed: bool
    grade: Optional[str] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoadmapProgressUpdate(BaseModel):
    """Roadmap item progress update request."""

    completed: bool
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "completed": True,
                "completed_at": "2024-01-12T00:00:00Z",
                "notes": "Sehr hilfreich für das Verständnis",
            }
        }


class PaginatedUniversitiesResponse(BaseModel):
    """Paginated universities response."""

    items: List[UniversityResponse]
    total: int
    limit: int
    offset: int


class PaginatedStudyProgramsResponse(BaseModel):
    """Paginated study programs response."""

    items: List[StudyProgramResponse]
    total: int


class PaginatedModulesResponse(BaseModel):
    """Paginated modules response."""

    items: List[ModuleResponse]
    total: int
    limit: int
    offset: int


class UserQuestionResponse(BaseModel):
    """User question response model."""

    id: int
    user_id: int
    question_text: str
    answer: bool
    career_tree_node_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedUserQuestionsResponse(BaseModel):
    """Paginated user questions response."""

    items: List[UserQuestionResponse]
    total: int
    limit: int
    offset: int

