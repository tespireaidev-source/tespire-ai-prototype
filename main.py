from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import logging

from service.llm import llm_reason
from service.period import resolve_period
from service.period_models import ResolvedPeriod
from service.memory import get_history, save_turn
from service.intent_router import route_intent
from service.response_builder import build_response
from service.period_guard import enforce_period
from service.logging_hook import log_ai_interaction


# ----------------------------------------------------
# Logging Setup
# ----------------------------------------------------
logger = logging.getLogger(__name__)


# ----------------------------------------------------
# FastAPI App
# ----------------------------------------------------
app = FastAPI(title="Tespire AI Prototype")


# ----------------------------------------------------
# INPUT CONTRACT
# ----------------------------------------------------
class AskContext(BaseModel):
    role: str
    school_id: str
    session_id: str
    student_id: Optional[str] = None


class AskRequest(BaseModel):
    question: str
    period: Optional[str] = None
    context: AskContext


# ----------------------------------------------------
# ROLE GUARD
# ----------------------------------------------------
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


# ----------------------------------------------------
# AI ENDPOINT
# ----------------------------------------------------
@app.post("/ask")
def ask_tespire_ai(payload: AskRequest):

    start_time = time.time()
    success = True
    response_text = None
    school_id = None
    resolved_period = None
    role = None

    try:
        # ----------------------------
        # Role Validation
        # ----------------------------
        role = role_guard(payload.context.role)

        # ----------------------------
        # Enforce Type Safety (school_id)
        # ----------------------------
        try:
            school_id = int(payload.context.school_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid school_id format"
            )

        # ----------------------------
        # Resolve Academic Period
        # ----------------------------
        resolved_period = resolve_period(
            school_id=school_id,
            period_input=payload.period
        )

        # ----------------------------
        # Enforce Period Access
        # ----------------------------
        resolved_period = enforce_period(role, resolved_period)

        # ----------------------------
        # Parent Guardrail
        # ----------------------------
        if role == "parent" and not payload.context.student_id:
            raise HTTPException(
                status_code=400,
                detail="Parent requests must include student_id"
            )

        # ----------------------------
        # Memory Retrieval
        # ----------------------------
        history = get_history(payload.context.session_id)

        # ----------------------------
        # Intent Classification
        # ----------------------------
        intent = llm_reason(
            payload.question,
            context=payload.context.dict(),
            history=history
        )

        if not isinstance(intent, str):
            intent = "unknown"
        else:
            intent = intent.strip().lower()

        # ----------------------------
        # Intent Routing
        # ----------------------------
        result = route_intent(
            intent=intent,
            context=payload.context,
            period=resolved_period
        )

        # ----------------------------
        # Save Conversation Turn
        # ----------------------------
        save_turn(
            payload.context.session_id,
            payload.question,
            result.answer,
            intent
        )

        # ----------------------------
        # Structured Response
        # ----------------------------
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

    # ----------------------------------------------------
    # Controlled Validation Errors (Transparent)
    # ----------------------------------------------------
    except HTTPException:
        success = False
        raise

    # ----------------------------------------------------
    # Unexpected System Errors (Structured Fallback)
    # ----------------------------------------------------
    except Exception as e:
        success = False
        logger.exception("Unexpected AI service failure")

        fallback_period = ResolvedPeriod(
            id=0,
            label="Unavailable",
            period_type="system"
        )

        final_response = build_response(
            answer="The AI service encountered an internal error.",
            supporting_metrics={},
            data_gaps="System error",
            suggested_actions=["Please try again later"],
            role=role if role else "unknown",
            period=fallback_period,
            intent="system",
            student_id=None,
        )

        response_text = final_response.answer
        return final_response

    # ----------------------------------------------------
    # Logging (Always Runs)
    # ----------------------------------------------------
    finally:
        execution_time_ms = int((time.time() - start_time) * 1000)

        session_term_id = None
        if resolved_period and isinstance(resolved_period, ResolvedPeriod):
            session_term_id = resolved_period.id

        log_ai_interaction(
            user_id=getattr(payload.context, "user_id", payload.context.session_id),
            role=role if role else payload.context.role,
            school_id=school_id if school_id is not None else payload.context.school_id,
            session_term_id=session_term_id,
            prompt=payload.question,
            response=response_text,
            success=success,
            execution_time_ms=execution_time_ms
        )
