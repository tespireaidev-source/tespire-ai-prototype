from typing import Dict, List


def infer_risks_and_trends(
    intent: str,
    supporting_metrics: Dict,
    scope_level: str
) -> List[str]:
    """
    Generates measurable, non-predictive insights
    based strictly on available metrics.

    - No future predictions
    - No subjective judgement
    - No hallucination
    - Zero values are treated as valid data
    """

    insights: List[str] = []

    # Attendance
    if intent == "attendance":
        rate = supporting_metrics.get("attendance_rate_percent")

        if rate is None:
            rate = supporting_metrics.get("attendance_rate")

        if rate is not None:
            if rate < 75:
                insights.append(
                    "Attendance rate is below 75%, which may indicate attendance risk."
                )
            elif rate >= 95:
                insights.append(
                    "Attendance rate is strong (95% or higher)."
                )

    # Performance
    elif intent == "performance":
        avg = supporting_metrics.get("average_score")

        if avg is not None:
            if avg < 50:
                insights.append(
                    "Average score is below 50%, which may indicate academic risk."
                )
            elif avg >= 75:
                insights.append(
                    "Average performance is strong (75% or higher)."
                )

    # Fees
    elif intent == "fees":
        outstanding = supporting_metrics.get("outstanding_amount")

        if outstanding is None:
            outstanding = supporting_metrics.get("outstanding")

        if outstanding is not None and outstanding > 0:
            insights.append(
                "There are outstanding fees that may require follow-up."
            )

    return insights