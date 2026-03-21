from service.database import supabase
from service.student_utils import get_student_full_name


def get_top_students(school_id: int, session_id: str, term_id: str):

    response = (
        supabase
        .table("student_term_results")
        .select("student_id, average_total")
        .eq("tenant_id", school_id)
        .eq("session_id", session_id)
        .eq("term_id", term_id)
        .order("average_total", desc=True)
        .limit(5)
        .execute()
    )

    data = response.data or []

    results = []

    for row in data:

        name = get_student_full_name(row.get("student_id"))

        results.append({
            "student": name if name else "Unknown Student",
            "score": row.get("average_total")
        })

    return results


def get_lowest_students(school_id: int, session_id: str, term_id: str):

    response = (
        supabase
        .table("student_term_results")
        .select("student_id, average_total")
        .eq("tenant_id", school_id)
        .eq("session_id", session_id)
        .eq("term_id", term_id)
        .order("average_total")
        .limit(5)
        .execute()
    )

    data = response.data or []

    results = []

    for row in data:

        name = get_student_full_name(row.get("student_id"))

        results.append({
            "student": name if name else "Unknown Student",
            "score": row.get("average_total")
        })

    return results