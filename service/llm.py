def llm_reason(question: str, context=None, history=None) -> str:

    question = question.lower()

    # Attendance
    if any(word in question for word in ["attendance", "present", "absent"]):
        return "attendance"

    # Payments 
    if any(word in question for word in ["fee", "fees", "payment", "paid", "outstanding"]):
        return "payments"

    # Performance 
    if any(word in question for word in ["performance", "score", "result", "grade"]):
        return "performance"

    # Enrollment 
    if any(word in question for word in ["enrollment", "enrolled", "students"]):
        return "enrollment"

    
    if history:
        last_turn = history[-1]
        last_intent = last_turn.get("intent")

        if len(question.split()) <= 6 and last_intent:
            return last_intent

    return "unknown"
