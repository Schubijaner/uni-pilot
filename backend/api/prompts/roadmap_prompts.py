"""Roadmap generation prompt templates."""

import json
from typing import List

from database.models import CareerTreeNode, Module, RoadmapItemType, StudyProgram, TopicField, UserProfile

# JSON Schema for structured roadmap response
ROADMAP_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Name of the roadmap"},
        "description": {
            "type": "string",
            "description": "Brief description of the roadmap",
        },
        "items": {
            "type": "array",
            "description": "List of roadmap items in hierarchical structure",
            "items": {
                "type": "object",
                "properties": {
                    "item_type": {
                        "type": "string",
                        "enum": [
                            "MODULE",
                            "COURSE",
                            "PROJECT",
                            "SKILL",
                            "BOOK",
                            "CERTIFICATE",
                            "INTERNSHIP",
                            "BOOTCAMP",
                            "CAREER",
                        ],
                        "description": "Type of roadmap item",
                    },
                    "title": {"type": "string", "description": "Title of the item"},
                    "description": {
                        "type": "string",
                        "description": "Description of what to learn/do",
                    },
                    "semester": {
                        "type": "integer",
                        "description": "Semester number (null if in semester break)",
                        "nullable": True,
                    },
                    "is_semester_break": {
                        "type": "boolean",
                        "description": "Whether this item is for semester break",
                    },
                    "order": {
                        "type": "integer",
                        "description": "Order within siblings (for sorting)",
                    },
                    "parent_id": {
                        "type": "integer",
                        "description": "ID of parent item (null for root items)",
                        "nullable": True,
                    },
                    "level": {
                        "type": "integer",
                        "description": "Depth in tree (0 = root)",
                    },
                    "is_leaf": {
                        "type": "boolean",
                        "description": "Whether this is a leaf node (career goal)",
                    },
                    "is_career_goal": {
                        "type": "boolean",
                        "description": "Whether this item represents a career goal (Beruf)",
                    },
                    "module_id": {
                        "type": "integer",
                        "description": "ID of university module (if item_type is MODULE)",
                        "nullable": True,
                    },
                    "is_important": {
                        "type": "boolean",
                        "description": "Whether this item is particularly important",
                    },
                },
                "required": [
                    "item_type",
                    "title",
                    "description",
                    "is_semester_break",
                    "order",
                    "level",
                    "is_leaf",
                    "is_career_goal",
                    "is_important",
                ],
            },
        },
    },
    "required": ["name", "description", "items"],
}


def generate_roadmap_prompt(
    study_program: StudyProgram,
    user_profile: UserProfile,
    topic_field: TopicField,
    available_modules: List[Module],
) -> str:
    """
    Generate prompt for roadmap generation.

    Args:
        study_program: StudyProgram database model
        user_profile: UserProfile database model
        topic_field: TopicField database model
        available_modules: List of available modules for the study program

    Returns:
        Prompt string for LLM
    """
    # Format modules as JSON for context
    modules_data = []
    for module in available_modules:
        modules_data.append(
            {
                "id": module.id,
                "name": module.name,
                "description": module.description or "",
                "type": module.module_type.value,
                "semester": module.semester,
            }
        )

    modules_json = json.dumps(modules_data, indent=2, ensure_ascii=False)

    # Current semester calculation
    current_semester = user_profile.current_semester or 1
    target_semesters = current_semester + 4  # Plan for next 4 semesters

    prompt = f"""Du bist ein Karriereberater für {study_program.name} Studierende.

Erstelle eine detaillierte, hierarchische Roadmap für das Karriereziel: {topic_field.name}

Kontext:
- Studiengang: {study_program.name} ({study_program.degree_type or 'Bachelor'})
- Aktuelles Semester: {current_semester}
- Bereits vorhandene Skills: {user_profile.skills or "Keine angegeben"}
- Themenfeld: {topic_field.name}
- Beschreibung: {topic_field.description or "Keine Beschreibung verfügbar"}

Verfügbare Module aus dem Modulhandbuch (noch NICHT abgeschlossen):
{modules_json}

WICHTIG: Diese Module sind noch nicht vom Studierenden abgeschlossen. 
Die Roadmap sollte diese Module in die Planung einbeziehen, da sie noch zu absolvieren sind.

WICHTIG - Die Roadmap muss eine HIERARCHISCHE STRUKTUR haben:
1. Root-Level Items: Semester-Blöcke (z.B. "Semester {current_semester}", "Semester {current_semester + 1}")
2. Child Items: Konkrete Lerninhalte (Module, Kurse, Skills, Projekte)
3. Leaf Nodes: Berufe (item_type = "CAREER", is_leaf = true, is_career_goal = true)

Struktur die Roadmap folgendermaßen:

1. Zeitlich organisiert nach Semestern (bis Semester {target_semesters}) und Semesterferien
2. Hierarchisch: Semester → Module/Skills → Beruf (Leaf Node)
3. Integriere verfügbare Module aus dem Modulhandbuch (verwende die IDs aus obiger Liste)
4. Empfehle zusätzliche Ressourcen:
   - Bücher (item_type: "BOOK")
   - Online-Kurse (item_type: "COURSE")
   - Projekte (item_type: "PROJECT")
   - Skills (item_type: "SKILL")
   - Praktika (item_type: "INTERNSHIP")
   - Bootcamps (item_type: "BOOTCAMP")
   - Zertifikate (item_type: "CERTIFICATE")

5. WICHTIG - item_type und is_semester_break:
   - Für Semesterferien: Verwende einen gültigen item_type (z.B. "COURSE", "PROJECT", "SKILL") 
     UND setze is_semester_break: true
   - "SEMESTER_BREAK" ist KEIN gültiger item_type!
   - Beispiel: {{"item_type": "COURSE", "title": "Online-Kurs in Python", "is_semester_break": true}}

6. WICHTIG: Die Endknoten (Leaf Nodes) müssen Berufe sein (item_type: "CAREER", is_career_goal: true)
   - Z.B. "Full Stack Developer", "Data Scientist", etc.
   - Diese sind die ZIELE der Roadmap

Struktur-Beispiel:
- Semester {current_semester} (level=0, parent_id=null)
  - Modul: Web Development (level=1, parent_id=<semester_id>)
    - Skill: HTML/CSS (level=2, parent_id=<web_dev_id>)
      - Full Stack Developer (level=3, parent_id=<skill_id>, is_leaf=true, is_career_goal=true, item_type="CAREER")

Gib die Antwort als JSON zurück mit folgendem Schema:
{json.dumps(ROADMAP_JSON_SCHEMA, indent=2, ensure_ascii=False)}

WICHTIG:
- Alle Items müssen korrekt verschachtelt sein (parent_id referenziert korrekte IDs)
- level muss korrekt sein (0 für Root, 1+ für verschachtelt)
- Mindestens ein Leaf Node (Beruf) pro Hauptpfad
- order: Sortierung bei Geschwister-Nodes (1, 2, 3, ...)

Antworte NUR mit dem JSON, keine zusätzlichen Erklärungen."""

    return prompt


def generate_roadmap_prompt_for_job(
    study_program: StudyProgram,
    user_profile: UserProfile,
    job: CareerTreeNode,
    available_modules: List[Module],
) -> str:
    """
    Generate prompt for roadmap generation based on a specific job.

    Args:
        study_program: StudyProgram database model
        user_profile: UserProfile database model
        job: CareerTreeNode database model (must be a leaf node)
        available_modules: List of available modules for the study program

    Returns:
        Prompt string for LLM
    """
    # Format modules as JSON for context
    modules_data = []
    for module in available_modules:
        modules_data.append(
            {
                "id": module.id,
                "name": module.name,
                "description": module.description or "",
                "type": module.module_type.value,
                "semester": module.semester,
            }
        )

    modules_json = json.dumps(modules_data, indent=2, ensure_ascii=False)

    # Current semester calculation
    current_semester = user_profile.current_semester or 1
    target_semesters = current_semester + 4  # Plan for next 4 semesters

    job_name = job.name
    job_description = job.description or "Keine Beschreibung verfügbar"

    prompt = f"""Du bist ein Karriereberater für {study_program.name} Studierende.

Erstelle eine detaillierte, hierarchische Roadmap für den Beruf: {job_name}

Kontext:
- Studiengang: {study_program.name} ({study_program.degree_type or 'Bachelor'})
- Aktuelles Semester: {current_semester}
- Bereits vorhandene Skills: {user_profile.skills or "Keine angegeben"}
- Zielberuf: {job_name}
- Berufsbeschreibung: {job_description}

Verfügbare Module aus dem Modulhandbuch (noch NICHT abgeschlossen):
{modules_json}

WICHTIG: Diese Module sind noch nicht vom Studierenden abgeschlossen. 
Die Roadmap sollte diese Module in die Planung einbeziehen, da sie noch zu absolvieren sind.

WICHTIG - Die Roadmap muss eine HIERARCHISCHE STRUKTUR haben:
1. Root-Level Items: Semester-Blöcke (z.B. "Semester {current_semester}", "Semester {current_semester + 1}")
2. Child Items: Konkrete Lerninhalte (Module, Kurse, Skills, Projekte)
3. Leaf Node: Der Zielberuf "{job_name}" (item_type = "CAREER", is_leaf = true, is_career_goal = true)

Struktur die Roadmap folgendermaßen:

1. Zeitlich organisiert nach Semestern (bis Semester {target_semesters}) und Semesterferien
2. Hierarchisch: Semester → Module/Skills → Beruf (Leaf Node: {job_name})
3. Integriere verfügbare Module aus dem Modulhandbuch (verwende die IDs aus obiger Liste)
4. Empfehle zusätzliche Ressourcen:
   - Bücher (item_type: "BOOK")
   - Online-Kurse (item_type: "COURSE")
   - Projekte (item_type: "PROJECT")
   - Skills (item_type: "SKILL")
   - Praktika (item_type: "INTERNSHIP")
   - Bootcamps (item_type: "BOOTCAMP")
   - Zertifikate (item_type: "CERTIFICATE")

5. WICHTIG - item_type und is_semester_break:
   - Für Semesterferien: Verwende einen gültigen item_type (z.B. "COURSE", "PROJECT", "SKILL") 
     UND setze is_semester_break: true
   - "SEMESTER_BREAK" ist KEIN gültiger item_type!
   - Beispiel: {{"item_type": "COURSE", "title": "Online-Kurs in Python", "is_semester_break": true}}

6. WICHTIG: Der Endknoten (Leaf Node) muss der Beruf "{job_name}" sein (item_type: "CAREER", is_career_goal: true)
   - Dies ist das ZIEL der Roadmap

Struktur-Beispiel:
- Semester {current_semester} (level=0, parent_id=null)
  - Modul: Web Development (level=1, parent_id=<semester_id>)
    - Skill: HTML/CSS (level=2, parent_id=<web_dev_id>)
      - {job_name} (level=3, parent_id=<skill_id>, is_leaf=true, is_career_goal=true, item_type="CAREER")

Gib die Antwort als JSON zurück mit folgendem Schema:
{json.dumps(ROADMAP_JSON_SCHEMA, indent=2, ensure_ascii=False)}

WICHTIG:
- Alle Items müssen korrekt verschachtelt sein (parent_id referenziert korrekte IDs)
- level muss korrekt sein (0 für Root, 1+ für verschachtelt)
- Der Leaf Node muss der Beruf "{job_name}" sein
- order: Sortierung bei Geschwister-Nodes (1, 2, 3, ...)

Antworte NUR mit dem JSON, keine zusätzlichen Erklärungen."""

    return prompt

