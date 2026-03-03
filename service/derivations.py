from typing import Optional, List, Dict


# Enrollment

def compute_enrollment_rate(
    total_students: int,
    active_students: int
) -> float:
    if total_students == 0:
        return 0.0

    return round((active_students / total_students) * 100, 2)


# Attendance

def compute_attendance_rate(
    present_count: int,
    total_sessions: int
) -> float:
    if total_sessions == 0:
        return 0.0

    return round((present_count / total_sessions) * 100, 2)


# Payment

def compute_outstanding_amount(
    total_due: float,
    total_paid: float
) -> float:
    return round(total_due - total_paid, 2)


# Performance

def compute_average(scores: List[float]) -> Optional[float]:
    if not scores:
        return None

    return round(sum(scores) / len(scores), 2)


def compute_high_low(scores: List[float]) -> Dict[str, Optional[float]]:
    if not scores:
        return {"highest": None, "lowest": None}

    return {
        "highest": max(scores),
        "lowest": min(scores)
    }