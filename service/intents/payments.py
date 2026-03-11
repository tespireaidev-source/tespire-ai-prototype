from service.metrics import get_payment_metrics
from service.intents.types import IntentResult
from service.period_models import ResolvedPeriod
from service.intents.scope import AccessScope


def handle_payments(scope: AccessScope, period: ResolvedPeriod) -> IntentResult:

    metrics = get_payment_metrics(
        school_id=scope.school_id,
        session_id=period.session_id,
        student_id=scope.student_id
    )

    total_due = metrics.get("total_due", 0)
    total_paid = metrics.get("total_paid", 0)
    outstanding = metrics.get("outstanding_amount", 0)
    records = metrics.get("records_found", 0)

    if records == 0:
        return IntentResult(
            answer="Verified payment data is unavailable or incomplete for this period.",
            supporting_metrics={},
            data_scope_used={
                "module": "payments",
                "period": period.label,
                "scope": "student-level" if scope.student_id else "school-level",
                "records_analysed": 0
            },
            data_gaps="No invoice records found.",
            suggested_actions=["Verify payment records"]
        )

    if scope.student_id:
        answer = (
            f"Total fees due for {period.label} are {total_due}, "
            f"{total_paid} has been paid and {outstanding} remains outstanding "
            f"based on {records} invoice records."
        )
    else:
        answer = (
            f"Total school fees due for {period.label} are {total_due}, "
            f"{total_paid} has been collected and {outstanding} remains outstanding "
            f"based on {records} invoice records."
        )

    return IntentResult(
        answer=answer,
        supporting_metrics={
            "total_due": total_due,
            "total_paid": total_paid,
            "outstanding_amount": outstanding,
            "records_used": records
        },
        data_scope_used={
            "module": "payments",
            "period": period.label,
            "scope": "student-level" if scope.student_id else "school-level",
            "records_analysed": records
        },
        data_gaps=None,
        suggested_actions=[]
    )
