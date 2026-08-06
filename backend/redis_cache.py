"""
Thin Redis-backed cache. If Redis isn't reachable, every function just
quietly does nothing (cache miss / no-op set) instead of blowing up the
request - the app works fine without Redis running, just uncached.
"""
import json
import redis
from config import Config

try:
    _client = redis.Redis(
        host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB,
        decode_responses=True, socket_connect_timeout=1,
    )
    _client.ping()
except Exception:
    _client = None


def cache_get(key):
    if not _client:
        return None
    try:
        raw = _client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def cache_set(key, value, ttl_seconds=60):
    if not _client:
        return
    try:
        _client.set(key, json.dumps(value), ex=ttl_seconds)
    except Exception:
        pass


def cache_delete_prefix(prefix):
    if not _client:
        return
    try:
        for key in _client.scan_iter(f"{prefix}*"):
            _client.delete(key)
    except Exception:
        pass
