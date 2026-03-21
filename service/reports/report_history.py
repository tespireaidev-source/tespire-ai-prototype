from service.database import supabase


def get_report_history(school_id: int):

    response = (
        supabase
        .table("session_terms")
        .select("session_id, term_id")
        .eq("tenant_id", school_id)
        .order("session_id", desc=True)
        .order("term_id", desc=True)
        .execute()
    )

    data = response.data or []

    history = []

    for r in data:

        history.append({
            "session": str(r.get("session_id")),
            "term": str(r.get("term_id")),
            "report_label": f"Session {r.get('session_id')} - Term {r.get('term_id')}"
        })

    return history
