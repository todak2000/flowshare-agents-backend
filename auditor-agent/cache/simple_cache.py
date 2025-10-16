"""
Simple in-memory cache with TTL
Provides caching functionality for historical data queries
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta


def utc_now() -> datetime:
    """Get timezone-aware UTC datetime"""
    return datetime.now(timezone.utc)


class CacheEntry:
    """Cache entry with expiration time"""

    def __init__(self, data: Any, ttl_seconds: int = 300):
        """
        Initialize cache entry

        Args:
            data: Data to cache
            ttl_seconds: Time-to-live in seconds (default: 5 minutes)
        """
        self.data = data
        self.expires_at = utc_now() + timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return utc_now() > self.expires_at


class SimpleCache:
    """
    Simple in-memory cache with TTL for historical data

    Features:
    - Time-based expiration (TTL)
    - Maximum size limit (LRU-like eviction)
    - Thread-safe for single-process use

    Note: This is per-instance cache. For distributed caching, use Redis.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize cache

        Args:
            max_size: Maximum number of entries (default: 100)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value if not expired

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            return entry.data
        elif entry:
            # Clean up expired entry
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """
        Set cache value with TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (default: 5 minutes)
        """
        # Prevent cache from growing too large
        if len(self._cache) >= self._max_size:
            self._evict_oldest()
        self._cache[key] = CacheEntry(value, ttl_seconds)

    def _evict_oldest(self) -> None:
        """Evict expired entries or oldest entry"""
        # First try to remove expired entries
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]

        # If still at capacity, remove one entry (FIFO)
        if len(self._cache) >= self._max_size and self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()

    def size(self) -> int:
        """Get current cache size"""
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "utilization": f"{len(self._cache)}/{self._max_size}"
        }
