from datetime import datetime
from typing import Dict, List, Optional

from service.period_models import ResolvedPeriod
from service.models import AskResponse
from service.prompts import get_guided_prompts
from service.followups import get_follow_up_prompts
from service.inference import infer_risks_and_trends
from service.drilldown import get_drilldown_options


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
) -> AskResponse:
    """
    Builds a structured AI response.

    Adds:
    - Role-based discovery prompts
    - Contextual follow-up prompts
    - Measurable inferred insights
    - Drill-down navigation options
    - Transparent scope metadata
    """

    scope_level = "child-level" if student_id else "school-level"

    follow_ups = get_follow_up_prompts(
        intent=intent,
        scope_level=scope_level,
        supporting_metrics=supporting_metrics
    )

    inferred = infer_risks_and_trends(
        intent=intent,
        supporting_metrics=supporting_metrics,
        scope_level=scope_level
    )

    drilldown = get_drilldown_options(
        intent=intent,
        scope_level=scope_level
    )

    return AskResponse(
        answer=answer,
        supporting_metrics=supporting_metrics,
        data_gaps=data_gaps,
        suggested_actions=suggested_actions or [],
        data_scope_used={
            "module": intent,
            "role": role,
            "period": period.label,
            "period_type": period.period_type,
            "scope": scope_level,
        },
        timestamp=datetime.utcnow(),
        guided_prompts=get_guided_prompts(role),
        follow_up_prompts=follow_ups,
        inferred_insights=inferred,
        drilldown_options=drilldown
    )
