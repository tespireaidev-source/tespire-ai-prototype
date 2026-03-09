from service.metrics import get_enrollment_metrics
from service.intents.types import IntentResult
from service.intents.scope import AccessScope
from service.period_models import ResolvedPeriod
from service.derivations import compute_enrollment_rate


def handle_enrollment(scope: AccessScope, period: ResolvedPeriod) -> IntentResult:

    metrics = get_enrollment_metrics(
        school_id=scope.school_id
    )

    total = metrics.get("total_students", 0)
    active = metrics.get("active_students", 0)

    if total == 0:
        return IntentResult(
            answer="Verified enrollment data is unavailable.",
            supporting_metrics={},
            data_gaps="No student records found.",
            suggested_actions=["Verify student registration data source"]
        )

    enrollment_rate = compute_enrollment_rate(total, active)

    if scope.student_id:
        answer = (
            f"Your child is enrolled. "
            f"The school's enrollment rate is {enrollment_rate}%."
        )
    else:
        answer = (
            f"There are {active} active students out of {total}. "
            f"The enrollment rate is {enrollment_rate}%."
        )

    return IntentResult(
        answer=answer,
        supporting_metrics={
            "total_students": total,
            "active_students": active,
            "enrollment_rate_percent": enrollment_rate
        },
        data_gaps=None,
        suggested_actions=[]
    )
