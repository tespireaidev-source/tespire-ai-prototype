from pydantic import BaseModel


class ResolvedPeriod(BaseModel):
    id: int
    session_id: int
    term_id: int
    label: str
    period_type: str
    