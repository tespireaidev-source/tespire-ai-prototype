def compute_trend(current_value, previous_value):
    """
    Safely compute percentage difference between two metrics.
    Returns (difference, direction).
    """

    if previous_value is None:
        return None, None

    difference = round(current_value - previous_value, 2)

    if difference > 0:
        direction = "improved"
    elif difference < 0:
        direction = "declined"
    else:
        direction = "remained stable"

    return abs(difference), direction