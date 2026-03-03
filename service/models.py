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
    guided_prompts: Optional[Dict[str, List[str]]] = None
    follow_up_prompts: Optional[List[str]] = None
    inferred_insights: Optional[List[str]] = None
    drilldown_options: Optional[List[str]] = None
    