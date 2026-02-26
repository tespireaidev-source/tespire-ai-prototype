from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from service.llm import llm_reason
from service.period import resolve_period
from service.period_models import ResolvedPeriod
from service.memory import get_history, save_turn
from service.intent_router import route_intent
from service.response_builder import build_response
from service.period_guard import enforce_period
import time
from service.logging_hook import log_ai_interaction



app = FastAPI(title="Tespire AI Prototype")


# INPUT CONTRACT

class AskContext(BaseModel):
    role: str
    school_id: str
    session_id: str
    student_id: Optional[str] = None


class AskRequest(BaseModel):
    question: str
    period: Optional[str] = None
    context: AskContext



# GUARDRAILS 

ALLOWED_ROLES = ["owner", "admin", "teacher", "parent"]


def role_guard(role: str) -> str:
    role = role.lower()
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Invalid role"
        )
    return role



@app.get("/")
def root():
    return {"message": "Tespire AI backend is running"}


# AI ENDPOINT

@app.post("/ask")
def ask_tespire_ai(payload: AskRequest):

    start_time = time.time()
    success = True
    response_text = None

    try:
        role = role_guard(payload.context.role)

        resolved_period = resolve_period(
            school_id=payload.context.school_id,
            requested_session_term_id=payload.period
        )

        resolved_period = enforce_period(role, resolved_period)

        if role == "parent" and not payload.context.student_id:
            raise HTTPException(
                status_code=400,
                detail="Parent requests must include student_id"
            )

        history = get_history(payload.context.session_id)

        intent = llm_reason(
            payload.question,
            context=payload.context.dict(),
            history=history
            )
        intent = intent.strip().lower()
        
        if intent not in ["enrollment", "attendance", "fees", "performance"]:
            intent = "unknown"

        result = route_intent(
            intent=intent,
            context=payload.context,
            period=resolved_period
        )

        save_turn(
            payload.context.session_id,
            payload.question,
            result.answer,
            intent
        )

        final_response = build_response(
            answer=result.answer,
            supporting_metrics=result.supporting_metrics,
            data_gaps=result.data_gaps,
            suggested_actions=result.suggested_actions,
            role=role,
            period=resolved_period,
            intent=intent,
            student_id=payload.context.student_id,
            )

        response_text = final_response.answer

        return final_response

    except Exception as e:
        success = False
        safe_role = role if "role" in locals() else "unknown"

        safe_period = (resolved_period if "resolved_period" in locals() else ResolvedPeriod(
            id=0,
            label="unknown",
            value="unknown",
            type="unknown"
            )
        )

        final_response = build_response(
            answer="The AI service encountered an internal error.",
            supporting_metrics={},
            data_gaps="System error",
            suggested_actions=["Please try again later"],
            role=safe_role,
            period=safe_period,
            intent="system",
            student_id=None,
            )
        
        response_text = final_response.answer

        return final_response

    finally:
        execution_time_ms = int((time.time() - start_time) * 1000)

        log_ai_interaction(
            user_id=getattr(payload.context, "user_id", payload.context.session_id),
            role=role if "role" in locals() else payload.context.role,
            school_id=payload.context.school_id,
            session_term_id=(
                resolved_period.id
                if "resolved_period" in locals()
                else None
            ),
            prompt=payload.question,
            response=response_text,
            success=success,
            execution_time_ms=execution_time_ms
        )
        