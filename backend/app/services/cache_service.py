"""Redis Distributed Caching Service.

Provides JSON serialization/deserialization, TTL enforcement, pattern-based
wildcard invalidation, and graceful failover when Redis is disconnected.
"""

import json
from typing import Any, Optional
import redis
from app.config.settings import get_settings
from app.config.logging import logger

settings = get_settings()


class CacheService:
    """Service encapsulating Redis key-value cache operations with graceful degradations."""

    def __init__(self):
        """Initialize Redis connection client with configured timeouts and retry options."""
        self.enabled = settings.CACHE_ENABLED
        self.default_ttl = settings.REDIS_TTL
        self._client: Optional[redis.Redis] = None

        if self.enabled:
            try:
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                    decode_responses=True,
                    protocol=2,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Redis client: {e}. Graceful fallback active.")
                self._client = None

    @property
    def client(self) -> Optional[redis.Redis]:
        """Access underlying Redis client instance or None if uninitialized."""
        return self._client

    def is_healthy(self) -> bool:
        """Check whether Redis server connection is actively reachable.

        Returns:
            bool: True if Redis PING succeeds, False otherwise.
        """
        if not self._client:
            return False
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        """Lookup cache key. Returns deserialized JSON or None if miss / unavailable.

        Args:
            key: Unique cache key string.

        Returns:
            Optional[Any]: Deserialized payload or None.
        """
        if not self._client or not self.enabled:
            return None
        try:
            value = self._client.get(key)
            if value is not None:
                logger.debug(f"[CACHE HIT] Key: {key}")
                return json.loads(value)
            logger.debug(f"[CACHE MISS] Key: {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key '{key}': {e}. Falling back to DB.")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Populate cache key with JSON serializable value and TTL.

        Args:
            key: Cache key string.
            value: JSON-serializable Python data structure.
            ttl: Optional TTL duration in seconds (defaults to REDIS_TTL).

        Returns:
            bool: True if key was set, False on error or disabled cache.
        """
        if not self._client or not self.enabled:
            return False
        try:
            expires = ttl if ttl is not None else self.default_ttl
            serialized = json.dumps(value, default=str)
            self._client.setex(key, expires, serialized)
            logger.debug(f"[CACHE SET] Key: {key}, TTL: {expires}s")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete specific cache key.

        Args:
            key: Key to evict.

        Returns:
            bool: True if command executed, False otherwise.
        """
        if not self._client or not self.enabled:
            return False
        try:
            self._client.delete(key)
            logger.debug(f"[CACHE DELETE] Key: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key '{key}': {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching wildcard pattern via SCAN.

        Args:
            pattern: Glob-style match pattern (e.g. 'customers:list:*').

        Returns:
            int: Number of evicted keys.
        """
        if not self._client or not self.enabled:
            return 0
        try:
            cursor = 0
            deleted_count = 0
            while True:
                cursor, keys = self._client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    deleted_count += self._client.delete(*keys)
                if cursor == 0:
                    break
            logger.debug(f"[CACHE INVALIDATE PATTERN] Pattern: '{pattern}', Deleted: {deleted_count}")
            return deleted_count
        except Exception as e:
            logger.warning(f"Cache delete_pattern error for '{pattern}': {e}")
            return 0

    def invalidate_customer_cache(self, customer_id: Optional[str] = None) -> None:
        """Invalidate all customer list caches and customer detail if given.

        Args:
            customer_id: Optional UUID string of specific customer.
        """
        if customer_id:
            self.delete(f"customers:detail:{customer_id}")
        self.delete_pattern("customers:list:*")
        self.invalidate_dashboard_cache()

    def invalidate_interaction_cache(self, interaction_id: Optional[str] = None) -> None:
        """Invalidate interaction and dashboard caches.

        Args:
            interaction_id: Optional UUID string of specific interaction.
        """
        if interaction_id:
            self.delete(f"interactions:detail:{interaction_id}")
        self.delete_pattern("interactions:list:*")
        self.invalidate_dashboard_cache()

    def invalidate_dashboard_cache(self) -> None:
        """Invalidate dashboard summary metrics."""
        self.delete("dashboard:summary")


cache_service = CacheService()

