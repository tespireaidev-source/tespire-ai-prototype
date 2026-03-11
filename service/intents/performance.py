from service.metrics import get_performance_metrics, get_previous_term_performance
from service.intents.types import IntentResult
from service.period_models import ResolvedPeriod
from service.intents.scope import AccessScope
from service.student_utils import get_student_full_name
from service.trend_utils import compute_trend


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
            data_scope_used={
                "module": "performance",
                "period": period.label,
                "scope": "student-level" if scope.student_id else "school-level",
                "records_analysed": 0
            },
            data_gaps="No academic results found.",
            suggested_actions=["Verify academic performance data source"]
        )

    previous_avg = get_previous_term_performance(
        scope.school_id,
        period.session_id,
        period.term_id
    )

    trend_diff, trend_direction = compute_trend(avg, previous_avg)

    trend_text = ""

    if trend_diff is not None:
        if trend_direction == "improved":
            trend_text = f" This represents a {trend_diff}% improvement compared to the previous term."
        elif trend_direction == "declined":
            trend_text = f" This represents a {trend_diff}% decline compared to the previous term."
        else:
            trend_text = " Performance remained stable compared to the previous term."

    # Child-level response
    if scope.student_id:

        student_name = get_student_full_name(scope.student_id)

        if student_name:
            answer = (
                f"{student_name}'s average performance score for {period.label} "
                f"is {avg}% based on {records} academic records.{trend_text}"
            )
        else:
            answer = (
                f"The student's average performance score for {period.label} "
                f"is {avg}% based on {records} academic records.{trend_text}"
            )

    # School-level response
    else:
        answer = (
            f"The overall average performance score for {period.label} "
            f"is {avg}% based on {records} academic records.{trend_text}"
        )

    return IntentResult(
        answer=answer,
        supporting_metrics=metrics,
        data_scope_used={
            "module": "performance",
            "period": period.label,
            "scope": "student-level" if scope.student_id else "school-level",
            "records_analysed": records
        },
        data_gaps=None,
        suggested_actions=[]
    )
