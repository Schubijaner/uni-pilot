"""Chat prompt templates for topic field and job conversations."""

from database.models import CareerTreeNode, TopicField


def get_chat_system_prompt(topic_field: TopicField) -> str:
    """
    Generate system prompt for chat based on topic field.

    Args:
        topic_field: TopicField database model

    Returns:
        System prompt string for LLM
    """
    # Use custom system prompt if available, otherwise generate one
    if topic_field.system_prompt:
        return topic_field.system_prompt

    # Default system prompt if none is set
    return f"""Du bist ein Experte für {topic_field.name}.

{topic_field.description or "Du hilfst Studierenden bei Fragen zu diesem Themenfeld."}

Deine Aufgabe:
- Erkläre das Themenfeld verständlich und kurz
- Beantworte Fragen präzise (maximal 300 Wörter)
- Gib praktische Hinweise zu Skills, Tools und Einstiegsmöglichkeiten
- Sei ermutigend und konstruktiv
- Beziehe dich auf universitäre Kontexte

Antworte immer auf Deutsch und in einem freundlichen, professionellen Ton."""


def get_chat_system_prompt_for_job(job: CareerTreeNode) -> str:
    """
    Generate system prompt for chat based on job (career tree node).

    Args:
        job: CareerTreeNode database model (must be a leaf node)

    Returns:
        System prompt string for LLM
    """
    job_name = job.name
    job_description = job.description or ""

    # Build system prompt for job-specific chat
    prompt = f"""Du bist ein Karriereberater und Experte für den Beruf "{job_name}".

{job_description if job_description else "Du hilfst Studierenden bei Fragen zu diesem Beruf und unterstützt sie bei der Karriereplanung."}

Deine Aufgabe:
- Erkläre den Beruf "{job_name}" verständlich und umfassend
- Beantworte Fragen präzise (maximal 300 Wörter)
- Gib praktische Hinweise zu:
  * Erforderlichen Skills und Kompetenzen
  * Tools und Technologien
  * Einstiegsmöglichkeiten und Karrierepfaden
  * Typischen Aufgaben und Verantwortlichkeiten
- Unterstütze den Nutzer bei der Auswahl des richtigen Karrierepfads
- Sei ermutigend und konstruktiv
- Beziehe dich auf universitäre Kontexte und Studiengänge

Antworte immer auf Deutsch und in einem freundlichen, professionellen Ton."""

    return prompt

