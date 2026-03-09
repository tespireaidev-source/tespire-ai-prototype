from service.intents.enrollment import handle_enrollment
from service.intents.attendance import handle_attendance
from service.intents.payments import handle_payments
from service.intents.performance import handle_performance
from service.intents.types import IntentResult
from service.intents.access import INTENT_ACCESS
from service.intents.child_scope import resolve_child_scope
from service.period_models import ResolvedPeriod


def route_intent(intent: str, context, period: ResolvedPeriod) -> IntentResult:

    
    role = (context.role or "").lower()
    intent = (intent or "").lower()

    allowed_roles = INTENT_ACCESS.get(intent)

    if not allowed_roles:
        return IntentResult(
            answer="I don't understand this question yet.",
            supporting_metrics={},
            data_gaps="Unknown intent",
            suggested_actions=["Try rephrasing your question"]
        )

    if role not in allowed_roles:
        return IntentResult(
            answer="You do not have permission to access this information.",
            supporting_metrics={},
            data_gaps="Access restricted",
            suggested_actions=[]
        )

    scope = resolve_child_scope(context)

    if not scope.school_id:
        return IntentResult(
            answer="Invalid request context.",
            supporting_metrics={},
            data_gaps="Missing school_id",
            suggested_actions=[]
        )

    
    if intent == "enrollment":
        return handle_enrollment(scope, period)

    if intent == "attendance":
        return handle_attendance(scope, period)

    if intent == "payments":
        return handle_payments(scope, period)

    if intent == "performance":
        return handle_performance(scope, period)

    return IntentResult(
        answer="I don't understand this question yet.",
        supporting_metrics={},
        data_gaps="Unknown intent",
        suggested_actions=["Try rephrasing your question"]
    )
