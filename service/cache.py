import time

CACHE_STORE = {}

DEFAULT_TTL = 60  


def get_cache(key: str):
    entry = CACHE_STORE.get(key)

    if not entry:
        return None

    value, expiry = entry

    if time.time() > expiry:
        del CACHE_STORE[key]
        return None

    return value


def set_cache(key: str, value, ttl: int = DEFAULT_TTL):
    expiry = time.time() + ttl
    CACHE_STORE[key] = (value, expiry)
