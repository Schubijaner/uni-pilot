"""Skills extraction router using Bedrock LLM."""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from api.models.skills import SkillsExtractRequest, SkillsExtractResponse, Skill
from api.services.llm_service import LLMService
from api.dependencies import get_db
import json
import logging

router = APIRouter(prefix="/api/v1/skills", tags=["skills"])
logger = logging.getLogger(__name__)

SKILLS_EXTRACTION_PROMPT = (
    "Extrahiere exakt 5 relevante technische Skills aus folgendem Text. "
    "Antworte ausschließlich im JSON-Format: {\"skills\":[{\"name\":...,\"value\":...}],\"confidence\":...}. "
    "Jeder Skill-Name soll ein einzelnes, gängiges Schlagwort sein (z.B. Python, React, SQL, Machine Learning, Git). "
    "Der Wert (value) ist eine Schätzung der Kompetenz (0-100). "
    "confidence ist eine Zahl zwischen 0 und 1. Keine weiteren Erklärungen, keine Codeblöcke."
)

@router.post("/extract", response_model=SkillsExtractResponse)
def extract_skills(
    req: SkillsExtractRequest,
    db: Session = Depends(get_db),
):
    llm = LLMService()
    prompt = f"{SKILLS_EXTRACTION_PROMPT}\n\nText: {req.text}"
    try:
        response = llm.chat(
            system_prompt=None,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        # Remove code fences if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        data = json.loads(response)
        # Defensive: Clamp values, ensure 5 skills
        skills = data.get("skills", [])
        skills = [
            Skill(
                name=s.get("name", ""),
                value=max(0, min(100, int(s.get("value", 0))))
            ) for s in skills if s.get("name")
        ]
        if len(skills) > 5:
            skills = skills[:5]
        confidence = data.get("confidence", 0.7)
        confidence = max(0, min(1, float(confidence)))
        if len(skills) < 1:
            raise ValueError("No skills extracted")
        return SkillsExtractResponse(skills=skills, confidence=confidence)
    except Exception as e:
        logger.error(f"Skills extraction failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Skills extraction failed: {e}")
