def build_full_name(first_name, middle_name, last_name):
    """
    Safely combines name parts into a full name.
    Handles missing middle names gracefully.
    """

    parts = [
        (first_name or "").strip(),
        (middle_name or "").strip(),
        (last_name or "").strip()
    ]

    return " ".join([p for p in parts if p])