from service.database import supabase
from service.name_utils import build_full_name


def get_student_full_name(student_id: str):
    """
    Fetch student record and construct full name.
    """

    if not student_id:
        return None

    record = (
        supabase
        .table("students")
        .select("first_name, middle_name, last_name")
        .eq("id", student_id)
        .limit(1)
        .execute()
    )

    if not record.data:
        return None

    student = record.data[0]

    return build_full_name(
        student.get("first_name"),
        student.get("middle_name"),
        student.get("last_name")
    )