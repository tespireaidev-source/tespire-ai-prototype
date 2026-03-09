from typing import Optional
from service.database import supabase
from service.derivations import compute_average, compute_high_low



# ENROLLMENT


def get_enrollment_metrics(school_id: int):

    response = (
        supabase
        .table("students")
        .select("status")
        .eq("school_id", school_id)
        .execute()
    )

    data = response.data or []

    total_students = len(data)

    active_students = len([
        s for s in data
        if (s.get("status") or "").lower() == "active"
    ])

    return {
        "total_students": total_students,
        "active_students": active_students,
        "records_found": len(data)
    }



# ATTENDANCE


def get_attendance_metrics(
    school_id: int,
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

    present_count = len([
        r for r in data
        if r.get("present") is True
    ])

    total_sessions = len(data)

    return {
        "present_count": present_count,
        "total_sessions": total_sessions,
        "records_found": len(data)
    }



# PAYMENTS 

def get_payment_metrics(
    school_id: int,
    session_id: int,
    student_id: Optional[str] = None
):

    query = (
        supabase
        .table("invoices")
        .select("amount, status")
        .eq("school_id", school_id)
        .eq("session_id", session_id)
        .eq("owner_type", "student")
    )

    if student_id:
        query = query.eq("owner_id", student_id)

    response = query.execute()

    data = response.data or []

    total_due = sum(
        (inv.get("amount") or 0)
        for inv in data
    )

    total_paid = sum(
        (inv.get("amount") or 0)
        for inv in data
        if (inv.get("status") or "").lower() == "paid"
    )

    outstanding_amount = total_due - total_paid

    return {
        "total_due": total_due,
        "total_paid": total_paid,
        "outstanding_amount": outstanding_amount,
        "records_found": len(data)
    }


# PERFORMANCE

def _fetch_submitted_performance_records(
    school_id: int,
    session_id: int,
    term_id: int,
    student_id: Optional[str] = None
):

    query = (
        supabase
        .table("student_term_results")
        .select("average_total")
        .eq("school_id", school_id)
        .eq("session_id", session_id)
        .eq("term_id", term_id)
    )

    if student_id:
        query = query.eq("student_id", student_id)

    response = query.execute()

    return response.data or []


def get_performance_metrics(
    school_id: int,
    session_id: int,
    term_id: int,
    student_id: Optional[str] = None
):

    records = _fetch_submitted_performance_records(
        school_id,
        session_id,
        term_id,
        student_id
    )

    if not records:
        return {
            "average_score": None,
            "records_used": 0,
            "highest_score": None,
            "lowest_score": None
        }

    scores = [
        r.get("average_total")
        for r in records
        if r.get("average_total") is not None
    ]

    if not scores:
        return {
            "average_score": None,
            "records_used": 0,
            "highest_score": None,
            "lowest_score": None
        }

    average_score = compute_average(scores)
    high_low = compute_high_low(scores)

    return {
        "average_score": average_score,
        "records_used": len(scores),
        "highest_score": high_low["highest"],
        "lowest_score": high_low["lowest"]
    }
