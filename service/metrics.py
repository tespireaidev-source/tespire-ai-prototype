from typing import Optional
import logging

from service.database import supabase
from service.derivations import compute_average, compute_high_low
from service.cache import get_cache, set_cache


logger = logging.getLogger(__name__)


# ENROLLMENT


def get_enrollment_metrics(school_id: int):

    cache_key = f"enrollment:{school_id}"

    cached = get_cache(cache_key)
    if cached is not None:
        logger.info("CACHE HIT: enrollment")
        return cached

    logger.info("CACHE MISS: enrollment")

    response = (
        supabase
        .table("students")
        .select("status")
        .eq("tenant_id", school_id)
        .execute()
    )

    data = response.data if response.data else []

    total_students = len(data)

    active_students = len([
        s for s in data
        if (s.get("status") or "").lower() == "active"
    ])

    result = {
        "total_students": total_students,
        "active_students": active_students,
        "records_found": len(data)
    }

    set_cache(cache_key, result)

    return result


# ATTENDANCE


def get_attendance_metrics(
    school_id: int,
    session_id: str,
    term_id: str,
    student_id: Optional[str] = None
):

    student_part = student_id or "all"
    cache_key = f"attendance:{school_id}:{session_id}:{term_id}:{student_part}"

    cached = get_cache(cache_key)
    if cached is not None:
        logger.info("CACHE HIT: attendance")
        return cached

    logger.info("CACHE MISS: attendance")

    query = (
        supabase
        .table("attendances")
        .select("status")
        .eq("tenant_id", school_id)
        .eq("session_id", session_id)
        .eq("term_id", term_id)
    )

    if student_id:
        query = query.eq("student_id", student_id)

    response = query.execute()

    data = response.data if response.data else []

    present_count = len([
        r for r in data
        if (r.get("status") or "").lower() == "present"
    ])

    total_sessions = len(data)

    result = {
        "present_count": present_count,
        "total_sessions": total_sessions,
        "records_found": len(data)
    }

    set_cache(cache_key, result)

    return result


# PAYMENTS


def get_payment_metrics(
    school_id: int,
    session_id: str,
    student_id: Optional[str] = None
):

    student_part = student_id or "all"
    cache_key = f"payments:{school_id}:{session_id}:{student_part}"

    cached = get_cache(cache_key)
    if cached is not None:
        logger.info("CACHE HIT: payments")
        return cached

    logger.info("CACHE MISS: payments")

    query = (
        supabase
        .table("invoices")
        .select("amount, status")
        .eq("tenant_id", school_id)
        .eq("session_id", session_id)
        .eq("owner_type", "student")
    )

    if student_id:
        query = query.eq("owner_id", student_id)

    response = query.execute()

    data = response.data if response.data else []

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

    result = {
        "total_due": total_due,
        "total_paid": total_paid,
        "outstanding_amount": outstanding_amount,
        "records_found": len(data)
    }

    set_cache(cache_key, result)

    return result


# PERFORMANCE


def _fetch_submitted_performance_records(
    school_id: int,
    session_id: str,
    term_id: str,
    student_id: Optional[str] = None
):

    query = (
        supabase
        .table("student_term_results")
        .select("average_total")
        .eq("tenant_id", school_id)
        .eq("session_id", session_id)
        .eq("term_id", term_id)
    )

    if student_id:
        query = query.eq("student_id", student_id)

    response = query.execute()

    return response.data if response.data else []


def get_performance_metrics(
    school_id: int,
    session_id: str,
    term_id: str,
    student_id: Optional[str] = None
):

    student_part = student_id or "all"
    cache_key = f"performance:{school_id}:{session_id}:{term_id}:{student_part}"

    cached = get_cache(cache_key)
    if cached is not None:
        logger.info("CACHE HIT: performance")
        return cached

    logger.info("CACHE MISS: performance")

    records = _fetch_submitted_performance_records(
        school_id,
        session_id,
        term_id,
        student_id
    )

    if not records:
        result = {
            "average_score": None,
            "records_used": 0,
            "highest_score": None,
            "lowest_score": None
        }
        set_cache(cache_key, result)
        return result

    scores = [
        r.get("average_total")
        for r in records
        if r.get("average_total") is not None
    ]

    if not scores:
        result = {
            "average_score": None,
            "records_used": 0,
            "highest_score": None,
            "lowest_score": None
        }
        set_cache(cache_key, result)
        return result

    average_score = compute_average(scores)
    high_low = compute_high_low(scores)

    result = {
        "average_score": average_score,
        "records_used": len(scores),
        "highest_score": high_low["highest"],
        "lowest_score": high_low["lowest"]
    }

    set_cache(cache_key, result)

    return result


# PREVIOUS TERM PERFORMANCE


def get_previous_term_performance(
    school_id: int,
    session_id: str,
    term_id: str
):

    cache_key = f"previous_performance:{school_id}:{session_id}:{term_id}"

    cached = get_cache(cache_key)
    if cached is not None:
        logger.info("CACHE HIT: previous_performance")
        return cached

    logger.info("CACHE MISS: previous_performance")

    try:
        previous_term = str(int(term_id) - 1)
    except ValueError:
        return None

    if int(previous_term) < 1:
        return None

    query = (
        supabase
        .table("student_term_results")
        .select("average_total")
        .eq("tenant_id", school_id)
        .eq("session_id", session_id)
        .eq("term_id", previous_term)
    )

    response = query.execute()

    data = response.data if response.data else []

    scores = [
        r.get("average_total")
        for r in data
        if r.get("average_total") is not None
    ]

    if not scores:
        return None

    result = compute_average(scores)

    set_cache(cache_key, result)

    return result
