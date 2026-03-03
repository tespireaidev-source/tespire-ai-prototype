from typing import Dict, List


def get_follow_up_prompts(
    intent: str,
    scope_level: str,
    supporting_metrics: Dict
) -> List[str]:
    """
    Returns contextual follow-up prompts
    based on intent, scope, and result metrics.
    """

    prompts: List[str] = []

    if intent == "enrollment":
        prompts.append("How does this compare to last term?")
        prompts.append("Show enrollment trend over the past year.")

    elif intent == "attendance":
        if scope_level == "school-level":
            prompts.append("Which classes have the lowest attendance?")
        else:
            prompts.append("Show monthly attendance breakdown.")

        prompts.append("Compare attendance with last term.")

    elif intent == "fees":
        outstanding = (
            supporting_metrics.get("outstanding")
            or supporting_metrics.get("outstanding_amount")
            or 0
        )

        if outstanding > 0:
            prompts.append("Which students have the highest outstanding fees?")

        prompts.append("Compare fee collection with last term.")

    elif intent == "performance":
        prompts.append("Show highest and lowest performing students.")
        prompts.append("Compare performance with last term.")

    return prompts
