from service.metrics import get_performance_metrics
from service.intents.types import IntentResult
from service.period_models import ResolvedPeriod
from service.intents.scope import AccessScope


def handle_performance(scope: AccessScope, period: ResolvedPeriod) -> IntentResult:

    metrics = get_performance_metrics(
        school_id=scope.school_id,
        session_term_id=period.id,
        student_id=scope.student_id
    )

    average_score = metrics.get("average_score")
    records_used = metrics.get("records_used", 0)
    highest = metrics.get("highest_score")
    lowest = metrics.get("lowest_score")

    # Guardrail
    if average_score is None:
        return IntentResult(
            answer="Verified performance data is unavailable for this period.",
            supporting_metrics={},
            data_gaps="No academic results submitted.",
            suggested_actions=["Verify academic performance data source"]
        )

    if scope.student_id:
        answer = (
            f"Your child's average performance score for {period.label} "
            f"is {average_score}%. "
            f"Based on {records_used} submitted record(s)."
        )
    else:
        answer = (
            f"The overall average performance score for {period.label} "
            f"is {average_score}%. "
            f"Based on {records_used} submitted record(s)."
        )

    return IntentResult(
        answer=answer,
        supporting_metrics={
            "average_score": average_score,
            "records_used": records_used,
            "highest_score": highest,
            "lowest_score": lowest
        },
        data_gaps=None,
        suggested_actions=[]
    )
