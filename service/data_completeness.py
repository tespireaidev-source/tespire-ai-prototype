def check_data_completeness(records_used: int, expected_records: int):
    """
    Determines if dataset is complete or partial.
    """

    if expected_records == 0:
        return None

    if records_used < expected_records:

        missing = expected_records - records_used

        return {
            "status": "incomplete",
            "message": f"{missing} expected records are missing."
        }

    return {
        "status": "complete",
        "message": None
    }