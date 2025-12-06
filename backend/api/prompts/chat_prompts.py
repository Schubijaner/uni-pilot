"""Chat prompt templates for topic field conversations."""

from database.models import TopicField


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

