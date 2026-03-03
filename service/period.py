from fastapi import HTTPException
from service.database import supabase
from service.period_models import ResolvedPeriod
from typing import Optional


def resolve_period(
    school_id: int,
    period_input: Optional[str]
) -> ResolvedPeriod:

    
    if period_input in [None, "current"]:

        record = (
            supabase.table("session_terms")
            .select("*")
            .eq("school_id", school_id)
            .eq("is_current", True)
            .limit(1)
            .execute()
        )

        if not record.data:
            raise HTTPException(
                status_code=400,
                detail="No active academic period configured for this school."
            )

        row = record.data[0]

        return ResolvedPeriod(
            id=row["id"],
            label=f"Session {row['session_id']} - Term {row['term_id']}",
            period_type="current"
        )

    
    if str(period_input).isdigit():

        record = (
            supabase.table("session_terms")
            .select("*")
            .eq("id", int(period_input))
            .eq("school_id", school_id)
            .limit(1)
            .execute()
        )

        if not record.data:
            raise HTTPException(
                status_code=400,
                detail="Invalid academic period for this school."
            )

        row = record.data[0]

        return ResolvedPeriod(
            id=row["id"],
            label=row.get("name") or f"Session {row['session_id']} - Term {row['term_id']}",
            period_type="explicit"
        )

    
    raise HTTPException(
        status_code=400,
        detail="Unsupported period format."
    )

