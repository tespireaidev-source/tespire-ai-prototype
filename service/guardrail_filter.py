from typing import Optional


PROMPT_INJECTION_KEYWORDS = [
    "ignore permissions",
    "bypass permissions",
    "override system",
    "show all data",
    "admin access"
]

RAW_DATA_KEYWORDS = [
    "database",
    "table",
    "schema",
    "sql",
    "query",
    "export data",
    "show records"
]

PREDICTION_KEYWORDS = [
    "next term",
    "next year",
    "predict",
    "forecast",
    "future"
]

VAGUE_PROMPTS = [
    "how are we doing",
    "give me insights",
    "summary",
    "status"
]


def evaluate_guardrails(question: str) -> Optional[str]:

    q = question.lower().strip()

    # Prompt injection protection
    if any(k in q for k in PROMPT_INJECTION_KEYWORDS):
        return "I can't perform actions that bypass system permissions."

    # Raw data exposure protection
    if any(k in q for k in RAW_DATA_KEYWORDS):
        return "I can summarise insights but can't expose raw database records."

    # Prediction blocking
    if any(k in q for k in PREDICTION_KEYWORDS):
        return "I can’t predict future outcomes. I can summarise past or current school data."

    # Clarification prompts
    if q in VAGUE_PROMPTS:
        return "You can ask about enrolment, attendance, fees, or academic performance."

    return None
