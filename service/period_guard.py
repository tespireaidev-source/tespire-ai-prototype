from fastapi import HTTPException
from service.period_models import ResolvedPeriod


def enforce_period(role: str, period: ResolvedPeriod) -> ResolvedPeriod:

    role = (role or "").lower()


    if role in ["owner", "admin"]:
        return period

    
    if role == "teacher":
        if period.period_type not in ["current", "recent"]:
            raise HTTPException(
                status_code=403,
                detail="Teachers can only access current or recent periods"
            )


    if role == "parent":
        if period.period_type != "current":
            raise HTTPException(
                status_code=403,
                detail="Parents can only access current period data"
            )

    return period
