"""Skills extraction request/response schemas."""
from typing import List
from pydantic import BaseModel, Field

class Skill(BaseModel):
    name: str
    value: int = Field(..., ge=0, le=100)

class SkillsExtractRequest(BaseModel):
    text: str

class SkillsExtractResponse(BaseModel):
    skills: List[Skill]
    confidence: float = Field(..., ge=0, le=1)
