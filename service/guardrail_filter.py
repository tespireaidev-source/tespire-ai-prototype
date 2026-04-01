from typing import Optional


class GuardrailResult:
    def __init__(self, allowed: bool, message: Optional[str] = None):
        self.allowed = allowed
        self.message = message


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


def evaluate_guardrails(question: str) -> GuardrailResult:

    q = (question or "").lower().strip()

    # Prompt injection protection
    if any(k in q for k in PROMPT_INJECTION_KEYWORDS):
        return GuardrailResult(
            allowed=False,
            message="I can't perform actions that bypass system permissions."
        )

    # Raw data exposure protection
    if any(k in q for k in RAW_DATA_KEYWORDS):
        return GuardrailResult(
            allowed=False,
            message="I can summarise insights but can't expose raw database records."
        )

    # Prediction blocking
    if any(k in q for k in PREDICTION_KEYWORDS):
        return GuardrailResult(
            allowed=False,
            message="I can’t predict future outcomes. I can summarise past or current school data."
        )

    # Clarification prompts
    if any(q == v or v in q for v in VAGUE_PROMPTS):
        return GuardrailResult(
            allowed=False,
            message="You can ask about enrolment, attendance, fees, or academic performance."
        )

    return GuardrailResult(allowed=True)
