import time
from dataclasses import dataclass
from threading import RLock
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class TTLCacheService:
    def __init__(self):
        self._store: dict[str, CacheEntry] = {}
        self._lock = RLock()

    def get(self, key: str) -> tuple[bool, Any]:
        now = time.time()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return False, None
            if entry.expires_at <= now:
                del self._store[key]
                return False, None
            return True, entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        ttl = max(ttl_seconds, 0)
        expires_at = time.time() + ttl
        with self._lock:
            self._store[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


cache_service = TTLCacheService()
