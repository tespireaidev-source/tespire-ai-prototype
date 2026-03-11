from service.metrics import get_performance_metrics
from service.database import supabase
from service.student_utils import get_student_full_name
from service.trend_utils import compute_trend
from service.metrics import get_previous_term_performance


def generate_term_academic_report(school_id, session_id, term_id):

    performance = get_performance_metrics(
        school_id=school_id,
        session_id=session_id,
        term_id=term_id
    )

    avg = performance.get("average_score")
    highest = performance.get("highest_score")
    lowest = performance.get("lowest_score")

    # Fetch individual student scores
    response = (
        supabase
        .table("student_term_results")
        .select("student_id, average_total")
        .eq("tenant_id", school_id)
        .eq("session_id", session_id)
        .eq("term_id", term_id)
        .execute()
    )

    records = response.data or []

    # Sort students by score
    sorted_scores = sorted(
        records,
        key=lambda x: x.get("average_total") or 0,
        reverse=True
    )

    # Top students
    top_students = []
    for r in sorted_scores[:3]:

        name = get_student_full_name(r["student_id"])

        top_students.append({
            "name": name,
            "score": r.get("average_total")
        })

    # At risk students (below 40)
    at_risk_students = []

    for r in sorted_scores:
        score = r.get("average_total")

        if score is not None and score < 40:

            name = get_student_full_name(r["student_id"])

            at_risk_students.append({
                "name": name,
                "score": score
            })

    # Trend analysis
    previous_avg = get_previous_term_performance(
        school_id,
        session_id,
        term_id
    )

    trend_diff, trend_direction = compute_trend(avg, previous_avg)

    insights = []

    if trend_diff is not None:

        if trend_direction == "improved":
            insights.append(
                f"Average performance improved by {trend_diff}% compared to the previous term."
            )

        elif trend_direction == "declined":
            insights.append(
                f"Average performance declined by {trend_diff}% compared to the previous term."
            )

        else:
            insights.append(
                "Academic performance remained stable compared to the previous term."
            )

    return {
        "summary": {
            "average_score": avg,
            "highest_score": highest,
            "lowest_score": lowest
        },
        "top_students": top_students,
        "at_risk_students": at_risk_students,
        "insights": insights
    }
