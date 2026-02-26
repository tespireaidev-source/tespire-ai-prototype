from datetime import datetime
from typing import Dict, List, Optional
from service.period_models import ResolvedPeriod
from service.models import AskResponse


def build_response(
    *,
    answer: str,
    supporting_metrics: Dict,
    role: str,
    period: ResolvedPeriod,
    intent: str,
    student_id: Optional[str],
    data_gaps: Optional[str] = None,
    suggested_actions: Optional[List[str]] = None,
):
    return AskResponse(
        answer=answer,
        supporting_metrics=supporting_metrics,
        data_gaps=data_gaps,
        suggested_actions=suggested_actions or [],
        data_scope_used={
            "module": intent,
            "role": role,
            "period": period.label,
            "period_type": period.type,
            "scope": "child-level" if student_id else "school-level",
        },
        timestamp=datetime.utcnow(),
    )