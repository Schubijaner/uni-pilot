"""Roadmap-related Pydantic schemas."""

import json
import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator

from database.models import RoadmapItemType


class TopSkill(BaseModel):
    """Schema for a top skill with score."""

    skill: str
    score: int  # 0-100

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        """Validate score is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v


class SkillImpact(BaseModel):
    """Schema for skill impact when completing a roadmap item."""

    skill: str
    impact: int  # 0-100

    @field_validator("impact")
    @classmethod
    def validate_impact(cls, v: int) -> int:
        """Validate impact is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError("Impact must be between 0 and 100")
        return v


class RoadmapItemBase(BaseModel):
    """Base schema for roadmap items."""

    item_type: RoadmapItemType
    title: str
    description: Optional[str] = None
    semester: int  # MUST NEVER be null
    is_semester_break: bool = False
    order: int
    level: int = 0
    is_leaf: bool = False
    is_career_goal: bool = False
    module_id: Optional[int] = None
    is_important: bool = False
    top_skills: Optional[List[TopSkill]] = None  # Only for leaf nodes (is_career_goal=true)
    skill_impact: Optional[List[SkillImpact]] = None  # For all items - impact on skills when completed


class RoadmapItemCreate(RoadmapItemBase):
    """Schema for creating roadmap items (with parent_id)."""

    parent_id: Optional[int] = None


class RoadmapItemResponse(RoadmapItemBase):
    """Roadmap item response model."""

    id: int
    roadmap_id: int
    parent_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RoadmapItemTreeResponse(RoadmapItemResponse):
    """Roadmap item with children (for tree structure)."""

    children: List["RoadmapItemTreeResponse"] = []

    class Config:
        from_attributes = True


# Update forward reference
RoadmapItemTreeResponse.model_rebuild()


class RoadmapGenerateRequest(BaseModel):
    """Request to generate a roadmap."""

    topic_field_id: int

    class Config:
        schema_extra = {
            "example": {
                "topic_field_id": 1,
            }
        }


class RoadmapResponse(BaseModel):
    """Roadmap response model (flat format)."""

    id: int
    topic_field_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: Optional[List[RoadmapItemResponse]] = None
    tree: Optional[RoadmapItemTreeResponse] = None  # Optional hierarchical tree structure
    target_skills: Optional[List[TopSkill]] = None  # Soll-Skills from leaf nodes (top_skills)
    current_skills: Optional[List[TopSkill]] = None  # Ist-Skills (current skill levels)

    class Config:
        from_attributes = True


class RoadmapTreeResponse(BaseModel):
    """Roadmap response with hierarchical tree structure."""

    id: int
    topic_field_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tree: Optional[RoadmapItemTreeResponse] = None
    career_goals: Optional[List[RoadmapItemResponse]] = None

    class Config:
        from_attributes = True


class UserRoadmapItemProgressResponse(BaseModel):
    """User progress on a roadmap item."""

    roadmap_item: RoadmapItemResponse
    completed: bool
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class RoadmapProgressResponse(BaseModel):
    """User's overall roadmap progress."""

    roadmap: dict  # Roadmap basic info
    items: List[UserRoadmapItemProgressResponse]
    progress_percentage: float

    class Config:
        schema_extra = {
            "example": {
                "roadmap": {
                    "id": 1,
                    "topic_field_id": 1,
                    "name": "Full Stack Development Roadmap",
                },
                "items": [],
                "progress_percentage": 50.0,
            }
        }


def parse_skill_data_from_description(description: Optional[str]) -> Optional[dict]:
    """
    Parse skill_impact from description field using placeholders.
    
    Args:
        description: Description string that may contain skill data
        
    Returns:
        Dictionary with skill_impact data or None if not found
    """
    if not description:
        return None
    
    # Look for __SKILL_DATA_START__ ... __SKILL_DATA_END__
    pattern = r"__SKILL_DATA_START__\s*(.*?)\s*__SKILL_DATA_END__"
    match = re.search(pattern, description, re.DOTALL)
    
    if match:
        try:
            skill_data = json.loads(match.group(1).strip())
            return skill_data
        except (json.JSONDecodeError, ValueError) as e:
            return None
    
    return None


def parse_current_skills_from_description(description: Optional[str]) -> Optional[List[TopSkill]]:
    """
    Parse current_skills from roadmap description field using placeholders.
    
    Args:
        description: Roadmap description string that may contain current_skills data
        
    Returns:
        List of TopSkill objects or None if not found
    """
    if not description:
        return None
    
    # Look for __CURRENT_SKILLS_START__ ... __CURRENT_SKILLS_END__
    pattern = r"__CURRENT_SKILLS_START__\s*(.*?)\s*__CURRENT_SKILLS_END__"
    match = re.search(pattern, description, re.DOTALL)
    
    if match:
        try:
            data = json.loads(match.group(1).strip())
            current_skills = data.get("current_skills", [])
            if current_skills:
                return [TopSkill(**skill) for skill in current_skills]
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            return None
    
    return None

