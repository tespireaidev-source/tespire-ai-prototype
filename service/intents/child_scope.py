from fastapi import HTTPException
from service.database import supabase
from service.intents.scope import AccessScope


def resolve_child_scope(context):

    school_id = context.school_id
    role = (context.role or "").lower()

    if not school_id:
        raise HTTPException(
            status_code=400,
            detail="Missing school context"
        )

    
    if role == "parent":

        if not context.student_id:
            raise HTTPException(
                status_code=400,
                detail="student_id is required for parent access"
            )

        record = (
            supabase
            .table("students")
            .select("id")
            .eq("id", context.student_id)
            .eq("school_id", school_id)
            .limit(1)
            .execute()
        )

        if not record.data:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized access to this student"
            )

        return AccessScope(
            school_id=school_id,
            student_id=context.student_id
        )


    return AccessScope(
        school_id=school_id,
        student_id=None
    )
