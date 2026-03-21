from service.database import supabase


def get_expected_performance_records(school_id: int, session_id: str, term_id: str):
    """
    Estimate expected number of performance records
    based on students and subjects.
    """

    students_response = (
        supabase
        .table("students")
        .select("id")
        .eq("tenant_id", school_id)
        .execute()
    )

    students = students_response.data or []

    subjects_response = (
        supabase
        .table("subjects")
        .select("id")
        .eq("tenant_id", school_id)
        .execute()
    )

    subjects = subjects_response.data or []

    student_count = len(students)
    subject_count = len(subjects)

    return student_count * subject_count