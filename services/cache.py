import json
import time

CACHE_TTL = 300
_in_memory_cache = {}

_redis_client = None
_redis_available = False

try:
    import redis
    _redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
        socket_timeout=1
    )
    _redis_client.ping()
    _redis_available = True
except Exception:
    _redis_available = False


def get_cache(key: str):
    """Retrieves cached prediction result from Redis or in-memory fallback."""
    if _redis_available and _redis_client:
        try:
            value = _redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception:
            pass

    # In-memory fallback
    item = _in_memory_cache.get(key)
    if item:
        val, expiry = item
        if time.time() < expiry:
            return val
        del _in_memory_cache[key]
    return None


def set_cache(key: str, value: dict, ttl: int = CACHE_TTL):
    """Saves prediction result to Redis or in-memory fallback."""
    if _redis_available and _redis_client:
        try:
            _redis_client.setex(key, ttl, json.dumps(value))
            return
        except Exception:
            pass

    # In-memory fallback
    _in_memory_cache[key] = (value, time.time() + ttl)
