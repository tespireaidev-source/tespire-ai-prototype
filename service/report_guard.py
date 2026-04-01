from fastapi import HTTPException


def enforce_report_access(role: str, report_type: str):

    role = role.lower()

    # Monthly operational report
    if report_type == "monthly_snapshot":

        if role not in ["owner", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access operational reports."
            )

    # Academic report
    elif report_type == "term_academic":

        if role not in ["owner", "admin", "teacher", "parent"]:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access academic reports."
            )

    else:
        raise HTTPException(
            status_code=400,
            detail="Unknown report type."
        )