from service.reports.term_academic_report import generate_term_academic_report


def get_authoritative_performance(school_id, session_id, term_id):
    """
    Returns official report value if available.
    """

    report = generate_term_academic_report(
        school_id,
        session_id,
        term_id
    )

    summary = report.get("summary", {})

    avg = summary.get("average_score")

    if avg is not None:
        return {
            "average_score": avg,
            "source": "official_report"
        }

    return None