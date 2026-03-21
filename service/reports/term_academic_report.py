from service.metrics import get_previous_term_performance
from service.database import supabase
from service.student_utils import get_student_full_name
from service.trend_utils import compute_trend


def generate_term_academic_report(
    school_id,
    session_id,
    term_id,
    student_id=None
):

    AT_RISK_THRESHOLD = 40
    HIGH_PERFORMANCE_THRESHOLD = 70

    term_clean = str(term_id).lower().replace("term", "").strip()

    response = (
        supabase
        .table("student_term_results")
        .select("""
            student_id,
            average_total,
            students!inner(
                class_id,
                classes!inner(name)
            )
        """)
        .eq("tenant_id", school_id)
        .eq("session_id", session_id)
        .eq("term_id", term_clean)
        .execute()
    )

    records = response.data or []

    # EMPTY DATA 
    if not records:
        return {
            "summary": {
                "average_score": None,
                "highest_score": None,
                "lowest_score": None,
                "trend": None
            },
            "top_students": [],
            "at_risk_students": [],
            "class_breakdown": [],
            "insights": ["No academic data available for this term."]
        }


    # student names
    student_ids = [r.get("student_id") for r in records if r.get("student_id")]

    names_map = {
        sid: get_student_full_name(sid)
        for sid in student_ids
    }

    # Score calculations
    scores = [r.get("average_total") or 0 for r in records]
    total_students = len(scores)

    avg = round(sum(scores) / total_students, 2)
    highest = max(scores)
    lowest = min(scores)


    # Sort students
    sorted_scores = sorted(
        records,
        key=lambda x: x.get("average_total") or 0,
        reverse=True
    )

    # Top Students 
    top_students = []

    for idx, r in enumerate(sorted_scores[:3], start=1):
        sid = r.get("student_id")
        score = r.get("average_total") or 0

        if not sid:
            continue

        top_students.append({
            "rank": idx,
            "name": names_map.get(sid, "Unknown Student"),
            "score": score
        })


    # At-Risk Students
    at_risk_students = []

    for r in sorted_scores:
        sid = r.get("student_id")
        score = r.get("average_total") or 0

        if not sid:
            continue

        if score < AT_RISK_THRESHOLD:
            at_risk_students.append({
                "name": names_map.get(sid, "Unknown Student"),
                "score": score
            })

    at_risk_count = len(at_risk_students)

    
    # Class-Level Breakdown
    class_data = {}

    for r in records:
        student_info = r.get("students")

        # Handle list/dict safely
        if isinstance(student_info, list):
            student_info = student_info[0] if student_info else {}

        class_info = student_info.get("classes") if student_info else {}

        if isinstance(class_info, list):
            class_info = class_info[0] if class_info else {}

        class_name = class_info.get("name") or "Unknown"
        score = r.get("average_total") or 0

        if class_name not in class_data:
            class_data[class_name] = {
                "scores": [],
                "at_risk": 0
            }

        class_data[class_name]["scores"].append(score)

        if score < AT_RISK_THRESHOLD:
            class_data[class_name]["at_risk"] += 1

    class_breakdown = []

    for class_name, data in class_data.items():
        scores_list = data["scores"]
        total = len(scores_list)

        avg_score = round(sum(scores_list) / total, 2) if total else 0
        at_risk_percent = round((data["at_risk"] / total) * 100, 1) if total else 0

        # Pass rate 
        pass_count = len([s for s in scores_list if s >= 50])
        pass_rate = round((pass_count / total) * 100, 1) if total else 0

        class_breakdown.append({
            "class": class_name,
            "average_score": avg_score,
            "students": total,
            "at_risk_percent": at_risk_percent,
            "pass_rate": pass_rate
        })

    
    class_breakdown = sorted(class_breakdown, key=lambda x: x["average_score"])


    # Trend Analysis
    previous_avg = get_previous_term_performance(
        school_id,
        session_id,
        term_id
    )

    if previous_avg is None:
        trend_diff, trend_direction = None, None
    else:
        trend_diff, trend_direction = compute_trend(avg, previous_avg)

    # Insights

    insights = []

    # Performance insight
    if avg < 50:
        insights.append(
            f"Average score is {avg}, which is below acceptable performance levels and requires attention."
        )
    elif avg >= 70:
        insights.append(
            f"Average score is {avg}, indicating strong overall academic performance."
        )
    else:
        insights.append(
            f"Average score is {avg}, indicating moderate academic performance."
        )

    # At-risk %
    at_risk_percent = round((at_risk_count / total_students) * 100, 1)

    if at_risk_count > 0:
        insights.append(
            f"{at_risk_percent}% of students are performing below expected level, indicating academic risk."
        )
    else:
        insights.append(
            "No students are currently identified as academically at risk."
        )

    # High performers
    high_performers = [s for s in scores if s >= HIGH_PERFORMANCE_THRESHOLD]
    high_perf_percent = round((len(high_performers) / total_students) * 100, 1)

    if high_performers:
        insights.append(
            f"{high_perf_percent}% of students are high-performing (score ≥ {HIGH_PERFORMANCE_THRESHOLD})."
        )

    # Weakest class
    if class_breakdown:
        weakest = class_breakdown[0]

        if weakest["average_score"] < 50:
            insights.append(
                f"{weakest['class']} is the weakest performing class with an average score of {weakest['average_score']}, requiring immediate academic intervention."
            )
        else:
            insights.append(
                f"{weakest['class']} has the lowest average score ({weakest['average_score']})."
            )

    # Best class 
    if class_breakdown:
        best_class = max(class_breakdown, key=lambda x: x["average_score"])
        insights.append(
            f"{best_class['class']} is the top-performing class with an average score of {best_class['average_score']}."
        )

    # Trend insight
    if trend_diff is not None:
        if trend_direction == "improved":
            insights.append(
                f"Performance improved by {trend_diff}% compared to the previous term."
            )
        elif trend_direction == "declined":
            insights.append(
                f"Performance declined by {trend_diff}% compared to the previous term."
            )
        else:
            insights.append(
                "Performance remained stable compared to the previous term."
            )

    # Final insight
    insights.append(f"{total_students} students analyzed this term.")


    # FINAL RESPONSE
    return {
        "summary": {
            "average_score": avg,
            "highest_score": highest,
            "lowest_score": lowest,
            "trend": {
                "direction": trend_direction,
                "percentage": trend_diff
            }
        },
        "top_students": top_students,
        "at_risk_students": at_risk_students,
        "class_breakdown": class_breakdown,
        "insights": insights
    }
