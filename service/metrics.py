from service.database import supabase
from typing import Optional


# ENROLLMENT

def get_enrollment_metrics(
    school_id: str
):

    response = (
        supabase
        .table("students")
        .select("id, status")
        .eq("school_id", school_id)
        .execute()
    )

    data = response.data or []

    total_students = len(data)
    active_students = len(
        [s for s in data if s.get("status") == "enrolled"]
    )

    enrollment_rate = (
        active_students / total_students
        if total_students > 0 else 0
    )

    return {
        "total_students": total_students,
        "active_students": active_students,
        "enrollment_rate": round(enrollment_rate, 2)
    }

# ATTENDANCE

def get_attendance_metrics(
    school_id: str,
    session_term_id: int,
    student_id: Optional[str] = None
):

    query = (
        supabase
        .table("attendances")
        .select("present")
        .eq("school_id", school_id)
        .eq("session_term_id", session_term_id)
    )

    if student_id:
        query = query.eq("student_id", student_id)

    response = query.execute()
    data = response.data or []

    if not data:
        return {"attendance_rate": None}

    present_count = len(
        [r for r in data if r.get("present") is True]
    )

    attendance_rate = present_count / len(data)

    return {
        "attendance_rate": round(attendance_rate, 2)
    }


# PAYMENTS

def get_payment_metrics(
    school_id: str,
    session_term_id: int,
    student_id: Optional[str] = None
):

    query = (
        supabase
        .table("payments")
        .select("amount, paid")
        .eq("school_id", school_id)
        .eq("session_term_id", session_term_id)
    )

    if student_id:
        query = query.eq("student_id", student_id)

    response = query.execute()
    data = response.data or []

    if not data:
        return {
            "total_due": 0,
            "total_paid": 0,
            "outstanding": 0
        }

    total_due = sum(
        r.get("amount", 0) for r in data
    )

    total_paid = sum(
        r.get("amount", 0)
        for r in data
        if r.get("paid") is True
    )

    outstanding = total_due - total_paid

    return {
        "total_due": total_due,
        "total_paid": total_paid,
        "outstanding": outstanding
    }

# PERFORMANCE

def _fetch_submitted_performance_records(
    school_id: str,
    session_term_id: int,
    student_id: Optional[str] = None
):
    query = (
        supabase
        .table("student_term_results")
        .select("average_score")
        .eq("school_id", school_id)
        .eq("session_term_id", session_term_id)
    )

    if student_id:
        query = query.eq("student_id", student_id)

    response = query.execute()
    return response.data or []


def get_performance_metrics(
    school_id: str,
    session_term_id: int,
    student_id: Optional[str] = None
):
    records = _fetch_submitted_performance_records(
        school_id,
        session_term_id,
        student_id
    )

    records_submitted = len(records)

    if records_submitted == 0:
        return {
            "average_score": None,
            "records_submitted": 0
        }

    avg = sum(
        r.get("average_score", 0)
        for r in records
    ) / records_submitted

    return {
        "average_score": round(avg, 2),
        "records_submitted": records_submitted
    }

