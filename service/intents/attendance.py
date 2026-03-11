from service.metrics import get_attendance_metrics
from service.intents.types import IntentResult
from service.period_models import ResolvedPeriod
from service.intents.scope import AccessScope
from service.derivations import compute_attendance_rate
from service.student_utils import get_student_full_name


def handle_attendance(scope: AccessScope, period: ResolvedPeriod) -> IntentResult:

    metrics = get_attendance_metrics(
        school_id=scope.school_id,
        session_term_id=period.id,
        student_id=scope.student_id
    )

    present = metrics.get("present_count", 0)
    total = metrics.get("total_sessions", 0)
    records = metrics.get("records_found", total)

    if total == 0:
        return IntentResult(
            answer="Verified attendance data is unavailable for this period.",
            supporting_metrics={},
            data_scope_used={
                "module": "attendance",
                "period": period.label,
                "scope": "student-level" if scope.student_id else "school-level",
                "records_analysed": 0
            },
            data_gaps="No attendance sessions recorded.",
            suggested_actions=["Verify attendance tracking system"]
        )

    attendance_rate = compute_attendance_rate(present, total)

    if scope.student_id:

        student_name = get_student_full_name(scope.student_id)

        if student_name:
            answer = (
                f"{student_name}'s attendance rate for {period.label} "
                f"is {attendance_rate}% based on {records} attendance records."
            )
        else:
            answer = (
                f"The student's attendance rate for {period.label} "
                f"is {attendance_rate}% based on {records} attendance records."
            )

    else:
        answer = (
            f"Overall attendance rate for {period.label} "
            f"is {attendance_rate}% based on {records} attendance records."
        )

    return IntentResult(
        answer=answer,
        supporting_metrics={
            "present_sessions": present,
            "total_sessions": total,
            "attendance_rate_percent": attendance_rate,
            "records_used": records
        },
        data_scope_used={
            "module": "attendance",
            "period": period.label,
            "scope": "student-level" if scope.student_id else "school-level",
            "records_analysed": records
        },
        data_gaps=None,
        suggested_actions=[]
    )
