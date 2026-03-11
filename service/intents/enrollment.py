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
    records = metrics.get("records_found", 0)

    if total == 0:
        return IntentResult(
            answer="Verified enrollment data is unavailable or incomplete.",
            supporting_metrics={},
            data_scope_used={
                "module": "enrollment",
                "period": period.label,
                "scope": "school-level",
                "records_analysed": 0
            },
            data_gaps="No student records found.",
            suggested_actions=["Verify student registration data"]
        )

    enrollment_rate = compute_enrollment_rate(total, active)

    answer = (
        f"There are {active} active students out of {total} for {period.label}, "
        f"representing an enrollment rate of {enrollment_rate}% "
        f"based on {records} student records."
    )

    return IntentResult(
        answer=answer,
        supporting_metrics={
            "total_students": total,
            "active_students": active,
            "enrollment_rate_percent": enrollment_rate,
            "records_used": records
        },
        data_scope_used={
            "module": "enrollment",
            "period": period.label,
            "scope": "school-level",
            "records_analysed": records
        },
        data_gaps=None,
        suggested_actions=[]
    )
