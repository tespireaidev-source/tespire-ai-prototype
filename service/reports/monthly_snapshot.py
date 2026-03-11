from service.metrics import (
    get_enrollment_metrics,
    get_attendance_metrics,
    get_payment_metrics,
    get_performance_metrics
)
from service.derivations import compute_enrollment_rate, compute_attendance_rate


def generate_monthly_snapshot(school_id, session_id, term_id):

    # Enrollment
    enrollment = get_enrollment_metrics(school_id)

    total_students = enrollment.get("total_students", 0)
    active_students = enrollment.get("active_students", 0)

    enrollment_rate = compute_enrollment_rate(total_students, active_students)

    # Attendance
    attendance = get_attendance_metrics(
        school_id=school_id,
        session_id=session_id,
        term_id=term_id
    )

    present = attendance.get("present_count", 0)
    total_sessions = attendance.get("total_sessions", 0)

    attendance_rate = compute_attendance_rate(present, total_sessions)

    # Payments
    payments = get_payment_metrics(
        school_id=school_id,
        session_id=session_id
    )

    total_due = payments.get("total_due", 0)
    total_paid = payments.get("total_paid", 0)
    outstanding = payments.get("outstanding_amount", 0)

    # Performance
    performance = get_performance_metrics(
        school_id=school_id,
        session_id=session_id,
        term_id=term_id
    )

    avg_score = performance.get("average_score")
    highest = performance.get("highest_score")
    lowest = performance.get("lowest_score")

    snapshot = {
        "enrollment": {
            "active_students": active_students,
            "total_students": total_students,
            "enrollment_rate_percent": enrollment_rate
        },
        "attendance": {
            "attendance_rate_percent": attendance_rate
        },
        "finance": {
            "total_due": total_due,
            "total_paid": total_paid,
            "outstanding_amount": outstanding
        },
        "academic": {
            "average_score": avg_score,
            "highest_score": highest,
            "lowest_score": lowest
        }
    }

    return snapshot