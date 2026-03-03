from pydantic import BaseModel


class ResolvedPeriod(BaseModel):
    id: int
    label: str
    period_type: str  