from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class AskResponse(BaseModel):
    answer: str
    supporting_metrics: Dict
    data_gaps: Optional[str]
    suggested_actions: List[str]
    data_scope_used: Dict
    timestamp: datetime
    