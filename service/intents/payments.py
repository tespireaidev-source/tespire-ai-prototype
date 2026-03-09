from service.metrics import get_payment_metrics
from service.intents.types import IntentResult
from service.period_models import ResolvedPeriod
from service.intents.scope import AccessScope
from service.derivations import compute_outstanding_amount


def handle_payments(scope: AccessScope, period: ResolvedPeriod) -> IntentResult:

    metrics = get_payment_metrics(
        school_id=scope.school_id,
        session_id=period.session_id,
        student_id=scope.student_id
    )

    total_due = metrics.get("total_due", 0)
    total_paid = metrics.get("total_paid", 0)
    records = metrics.get("records_found", 0)

    if records == 0:
        return IntentResult(
            answer="Verified payment data is unavailable for this period.",
            supporting_metrics={},
            data_gaps="No invoice records found.",
            suggested_actions=["Verify invoice or payment records"]
        )

    outstanding = compute_outstanding_amount(total_due, total_paid)

    if scope.student_id:
        answer = (
            f"Your child's total fees due are {total_due}. "
            f"{total_paid} has been paid and {outstanding} remains outstanding."
        )
    else:
        answer = (
            f"Total school fees due are {total_due}. "
            f"{total_paid} has been collected and {outstanding} remains outstanding."
        )

    return IntentResult(
        answer=answer,
        supporting_metrics={
            "total_due": total_due,
            "total_paid": total_paid,
            "outstanding_amount": outstanding
        },
        data_gaps=None,
        suggested_actions=[]
    )
