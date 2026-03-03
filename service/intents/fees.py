from service.metrics import get_payment_metrics
from service.intents.types import IntentResult
from service.period_models import ResolvedPeriod
from service.intents.scope import AccessScope
from service.derivations import compute_outstanding_amount


def handle_fees(scope: AccessScope, period: ResolvedPeriod) -> IntentResult:

    metrics = get_payment_metrics(
        school_id=scope.school_id,
        session_term_id=period.id,
        student_id=scope.student_id
    )

    records_found = metrics.get("records_found", 0)

    if records_found == 0:
        return IntentResult(
            answer="Verified fee data is unavailable for this period.",
            supporting_metrics={},
            data_gaps="No payment records found.",
            suggested_actions=["Verify fee management system"]
        )

    total_due = metrics.get("total_due", 0)
    total_paid = metrics.get("total_paid", 0)

    outstanding = compute_outstanding_amount(total_due, total_paid)

    if scope.student_id:
        answer = (
            f"Your child's total fees for {period.label} are {total_due}, "
            f"with {total_paid} paid and {outstanding} outstanding."
        )
    else:
        answer = (
            f"Total school fees for {period.label} are {total_due}, "
            f"with {total_paid} collected and {outstanding} outstanding."
        )

    return IntentResult(
        answer=answer,
        supporting_metrics={
            "total_due": total_due,
            "total_paid": total_paid,
            "outstanding_amount": outstanding,
            "records_found": records_found
        },
        data_gaps=None,
        suggested_actions=[]
    )
