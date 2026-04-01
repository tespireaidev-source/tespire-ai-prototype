from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import time
import logging

from service.auth import verify_token

from service.llm import llm_reason
from service.period import resolve_period
from service.period_models import ResolvedPeriod
from service.memory import get_history, save_turn
from service.intent_router import route_intent
from service.response_builder import build_response
from service.period_guard import enforce_period
from service.logging_hook import log_ai_interaction
from service.drilldown_executor import get_top_students, get_lowest_students
from service.ai_access_control import is_ai_enabled_for_role
from service.guardrail_filter import evaluate_guardrails

from service.reports.monthly_snapshot import generate_monthly_snapshot
from service.reports.term_academic_report import generate_term_academic_report
from service.reports.report_history import get_report_history
from service.report_guard import enforce_report_access
from service.rate_limiter import is_rate_limited



# LOGGING SETUP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tespire AI Prototype")



# REQUEST MODELS

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
        raise HTTPException(status_code=403, detail="Invalid role")

    return role


@app.get("/")
def root():
    return {"message": "Tespire AI backend is running"}



# AI QUERY ENDPOINT 

@app.post("/ask")
def ask_tespire_ai(payload: AskRequest, request: Request):

    start_time = time.time()
    success = True
    response_text = None
    resolved_period: Optional[ResolvedPeriod] = None
    role = None
    school_id = None

    try:
        # entry log
        logger.info(f"Incoming request | session_id={payload.context.session_id}")

        # auth check
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            raise HTTPException(status_code=401, detail="Invalid Authorization format")

        token = parts[1]

        user = verify_token(token)

        if user == "expired":
            raise HTTPException(status_code=401, detail="Token expired")

        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # use JWT values
        role = user.get("role")
        school_id = user.get("school_id")

        if not role or not school_id:
            raise HTTPException(status_code=403, detail="Invalid user context")

        role = role_guard(role)

    
        # RATE LIMITING 
        
        user_id = user.get("sub") or getattr(payload.context, "session_id", None)

        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user identifier")

        if is_rate_limited(user_id):
            logger.warning(f"Rate limit hit | user_id={user_id}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please slow down."
            )

        
        # AI ACCESS CONTROL

        if not is_ai_enabled_for_role(school_id, role):
            raise HTTPException(
                status_code=403,
                detail="AI access is currently disabled for this role."
            )


        # PERIOD RESOLUTION
        
        resolved_period = resolve_period(
            school_id=school_id,
            period_input=payload.period
        )

        resolved_period = enforce_period(role, resolved_period)

    
        # ROLE VALIDATION
        
        if role == "parent" and not payload.context.student_id:
            raise HTTPException(
                status_code=400,
                detail="Parent requests must include student_id"
            )

        
        # GUARDRAILS
        
        guardrail = evaluate_guardrails(payload.question)

        if not guardrail.allowed:
            logger.info(f"Guardrail triggered | session_id={payload.context.session_id}")

            return build_response(
                answer=guardrail.message,
                supporting_metrics={},
                data_gaps=None,
                suggested_actions=[],
                role=role,
                period=resolved_period,
                intent="guardrail",
                student_id=payload.context.student_id,
            )

        
        # MEMORY AND INTENT
        
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

        # intent log
        logger.info(
            f"Intent detected | intent={intent} | session_id={payload.context.session_id}"
        )

    
        # execution
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

        # response log
        logger.info(
            f"Response generated | session_id={payload.context.session_id}"
        )

        return final_response

    except HTTPException:
        success = False
        raise

    except Exception:
        success = False

        # error log
        logger.exception(
            f"Unexpected AI service failure | session_id={payload.context.session_id} | question={payload.question}"
        )

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

        # performance log
        logger.info(
            f"Request completed | session_id={payload.context.session_id} | "
            f"success={success} | execution_time_ms={execution_time_ms}"
        )

        # central log storage
        log_ai_interaction(
            user_id=payload.context.session_id,
            role=role if role else "unknown",
            school_id=school_id if school_id else 0,
            session_term_id=session_term_id,
            prompt=payload.question,
            response=response_text,
            success=success,
            execution_time_ms=execution_time_ms
        )



# MONTHLY SNAPSHOT REPORT

@app.get("/reports/monthly")
def get_monthly_snapshot(role: str, school_id: int, session_id: str, term_id: str):

    role = role_guard(role)
    enforce_report_access(role, "monthly_snapshot")

    snapshot = generate_monthly_snapshot(school_id, session_id, term_id)
    term_clean = str(term_id).lower().replace("term", "").strip()

    return {
        "report": "Monthly Operational Snapshot",
        "period": f"Session {session_id} - Term {term_clean}",
        "snapshot": snapshot
    }


# ACADEMIC TERM REPORT

@app.get("/reports/term-academic")
def get_term_academic_report(
    role: str,
    school_id: int,
    session_id: str,
    term_id: str,
    student_id: Optional[str] = None
):

    role = role_guard(role)
    enforce_report_access(role, "term_academic")

    if role == "parent" and not student_id:
        raise HTTPException(status_code=400, detail="Parents must provide student_id")

    report = generate_term_academic_report(
        school_id, session_id, term_id, student_id
    )

    return {
        "report": "End-of-Term Academic Report",
        "period": f"Session {session_id} - Term {term_id}",
        "data": report
    }


# REPORT HISTORY

@app.get("/reports/history")
def get_reports_history(role: str, school_id: int):

    role = role_guard(role)
    enforce_report_access(role, "term_academic")

    history = get_report_history(school_id)

    return {
        "report": "Available Report History",
        "school_id": school_id,
        "reports": history
    }


# DRILLDOWN

@app.post("/drilldown")
def drilldown(role: str, type: str, school_id: int, session_id: str, term_id: str):

    role = role_guard(role)

    if type == "top_students":
        data = get_top_students(school_id, session_id, term_id)
        return {"drilldown": "Top Performing Students", "data": data}

    if type == "lowest_students":
        data = get_lowest_students(school_id, session_id, term_id)
        return {"drilldown": "Lowest Performing Students", "data": data}

    raise HTTPException(
        status_code=400,
        detail="Invalid drilldown type. use 'top_students' or 'lowest_students'."
    )

