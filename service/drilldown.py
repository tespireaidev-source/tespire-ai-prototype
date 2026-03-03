from typing import List


def get_drilldown_options(intent: str, scope_level: str) -> List[str]:
    """
    Returns safe drill-down navigation options.

    - No raw database exposure
    - No direct table references
    - Role-safe
    - Scope-aware
    """

    options: List[str] = []

    if intent == "attendance":
        if scope_level == "school-level":
            options.append("Drill down into class-level attendance.")
        else:
            options.append("Drill down into subject-level attendance.")

    elif intent == "performance":
        if scope_level == "school-level":
            options.append("Drill down into class performance breakdown.")
        else:
            options.append("Drill down into subject performance breakdown.")

    elif intent == "fees":
        if scope_level == "school-level":
            options.append("Drill down into class-level fee breakdown.")
        else:
            options.append("Drill down into payment history.")

    elif intent == "enrollment":
        options.append("Drill down into class enrollment distribution.")

    return options