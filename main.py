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

from service.reports.monthly_snapshot import generate_monthly_snapshot
from service.reports.term_academic_report import generate_term_academic_report


logger = logging.getLogger(__name__)

app = FastAPI(title="Tespire AI Prototype")


class AskContext(BaseModel):
    role: str
    school_id: int
    session_id: str
    student_id: Optional[str] = None


class AskRequest(BaseModel):
    question: str
    period: Optional[str] = None
    context: AskContext


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



# AI QUERY ENDPOINT


@app.post("/ask")
def ask_tespire_ai(payload: AskRequest):

    start_time = time.time()
    success = True
    response_text = None
    resolved_period: Optional[ResolvedPeriod] = None
    role = None

    try:

        role = role_guard(payload.context.role)

        school_id = payload.context.school_id

        resolved_period = resolve_period(
            school_id=school_id,
            period_input=payload.period
        )

        resolved_period = enforce_period(role, resolved_period)

        # Parent Guardrail
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

        allowed_intents = {
            "enrollment",
            "attendance",
            "payments",
            "performance"
        }

        if not isinstance(intent, str):
            intent = "unknown"
        else:
            intent = intent.strip().lower()

        if intent not in allowed_intents:
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


    except HTTPException:
        success = False
        raise


    except Exception:

        success = False

        logger.exception("Unexpected AI service failure")

        fallback_period = ResolvedPeriod(
            id=0,
            session_id="unknown",
            term_id="unknown",
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


    finally:

        execution_time_ms = int((time.time() - start_time) * 1000)

        session_term_id = None
        if resolved_period:
            session_term_id = resolved_period.id

        log_ai_interaction(
            user_id=payload.context.session_id,
            role=role if role else payload.context.role,
            school_id=payload.context.school_id,
            session_term_id=session_term_id,
            prompt=payload.question,
            response=response_text,
            success=success,
            execution_time_ms=execution_time_ms
        )



# MONTHLY SNAPSHOT REPORT

@app.get("/reports/monthly")
def get_monthly_snapshot(
    school_id: int,
    session_id: str,
    term_id: str
):

    snapshot = generate_monthly_snapshot(
        school_id=school_id,
        session_id=session_id,
        term_id=term_id
    )

    return {
        "report": "Monthly Operational Snapshot",
        "period": f"Session {session_id} - Term {term_id}",
        "snapshot": snapshot
    }

#TERM ACADEMIC REPORTS

@app.get("/reports/term-academic")

def get_term_academic_report(
    school_id: int,
    session_id: str,
    term_id: str
):

    report = generate_term_academic_report(
        school_id,
        session_id,
        term_id
    )

    return {
        "report": "End-of-Term Academic Report",
        "period": f"Session {session_id} - Term {term_id}",
        "data": report
    }
