from service.metrics import get_performance_metrics
from service.intents.types import IntentResult
from service.period_models import ResolvedPeriod
from service.intents.scope import AccessScope


def handle_performance(scope: AccessScope, period: ResolvedPeriod) -> IntentResult:

    metrics = get_performance_metrics(
        school_id=scope.school_id,
        session_id=period.session_id,
        term_id=period.term_id,
        student_id=scope.student_id
    )

    avg = metrics.get("average_score")
    records = metrics.get("records_used", 0)

    if avg is None:
        return IntentResult(
            answer="Verified performance data is unavailable for this period.",
            supporting_metrics={},
            data_gaps="No academic results found.",
            suggested_actions=["Verify academic performance data source"]
        )

    if scope.student_id:
        answer = (
            f"Your child's average performance score for {period.label} "
            f"is {avg}."
        )
    else:
        answer = (
            f"The overall average performance score for {period.label} "
            f"is {avg}."
        )

    return IntentResult(
        answer=answer,
        supporting_metrics=metrics,
        data_gaps=None,
        suggested_actions=[]
    )
