import time
from collections import defaultdict

REQUEST_LOG = defaultdict(list)

MAX_REQUESTS = 10
WINDOW_SECONDS = 10


def is_rate_limited(user_id: str) -> bool:
    now = time.time()
    timestamps = REQUEST_LOG[user_id]

    timestamps[:] = [t for t in timestamps if now - t < WINDOW_SECONDS]

    if len(timestamps) >= MAX_REQUESTS:
        return True

    timestamps.append(now)
    return False
