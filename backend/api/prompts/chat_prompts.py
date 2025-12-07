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


def generate_topic_field_greeting_prompt(topic_field: TopicField) -> str:
    """
    Generate a prompt for creating a funny, topic-field-specific greeting with a custom assistant name.

    Args:
        topic_field: TopicField database model

    Returns:
        Prompt string for LLM to generate greeting
    """
    topic_name = topic_field.name
    topic_description = topic_field.description or ""

    prompt = f"""Erstelle eine kurze, witzige und relevante Begrüßung für einen Chat-Assistenten, der sich auf das Themenfeld "{topic_name}" spezialisiert hat.

{topic_description if topic_description else ""}

Anforderungen:
1. Erfinde einen kreativen, witzigen Assistenten-Namen, der zum Themenfeld "{topic_name}" passt (z.B. "Alex der Algorithmus-Architekt" für Algorithmen, "Dana die Daten-Detektivin" für Data Science)
2. Die Begrüßung soll:
   - Maximal 3-4 Sätze lang sein
   - Witzig und einladend sein
   - Relevante Aspekte des Themenfelds "{topic_name}" erwähnen
   - Den Assistenten-Namen natürlich einbauen
   - Auf Deutsch sein
   - Freundlich und motivierend klingen

Format: Beginne direkt mit der Begrüßung, inklusive des Assistenten-Namens. Keine zusätzlichen Erklärungen.

Beispiel für "Machine Learning":
"Hallo! Ich bin Finn, der ML-Magier! 🎩 Ich helfe dir dabei, die Geheimnisse des maschinellen Lernens zu entschlüsseln und deine ersten Modelle zu trainieren. Lass uns gemeinsam deinen Weg in die Welt der KI gestalten!"

Erstelle jetzt eine ähnliche Begrüßung für "{topic_name}":"""

    return prompt


def generate_job_greeting_prompt(job: CareerTreeNode) -> str:
    """
    Generate a prompt for creating a funny, job-specific greeting with a custom assistant name.

    Args:
        job: CareerTreeNode database model (must be a leaf node)

    Returns:
        Prompt string for LLM to generate greeting
    """
    job_name = job.name
    job_description = job.description or ""

    prompt = f"""Erstelle eine kurze, witzige und relevante Begrüßung für einen Chat-Assistenten, der sich auf den Beruf "{job_name}" spezialisiert hat.

{job_description if job_description else ""}

Anforderungen:
1. Erfinde einen kreativen, witzigen Assistenten-Namen, der zum Beruf "{job_name}" passt (z.B. "Alex der Algorithmus-Architekt" für Algorithm Engineer, "Dana die Daten-Detektivin" für Data Scientist)
2. Die Begrüßung soll:
   - Maximal 3-4 Sätze lang sein
   - Witzig und einladend sein
   - Relevante Aspekte des Berufs "{job_name}" erwähnen
   - Den Assistenten-Namen natürlich einbauen
   - Auf Deutsch sein
   - Freundlich und motivierend klingen

Format: Beginne direkt mit der Begrüßung, inklusive des Assistenten-Namens. Keine zusätzlichen Erklärungen.

Beispiel für "Full Stack Developer":
"Hallo! Ich bin Finn, der Full Stack Virtuose! 🚀 Ich helfe dir dabei, sowohl Frontend als auch Backend zu meistern und die perfekte Balance zwischen Design und Funktionalität zu finden. Lass uns gemeinsam deinen Weg zum Full Stack Developer gestalten!"

Erstelle jetzt eine ähnliche Begrüßung für "{job_name}":"""

    return prompt

