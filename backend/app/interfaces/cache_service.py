"""Cache Service Interface Protocol.

Defines the contract for key-value caching engines (Redis / In-memory fallback),
providing cache retrieval, mutation, and entity invalidation operations.
"""

from typing import Any, Optional, Protocol


class ICacheService(Protocol):
    """Redis/Memory cache service protocol."""

    def get(self, key: str) -> Optional[Any]:
        """Fetch and deserialize a value from cache by key."""
        ...

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Serialize and persist a key-value pair with TTL."""
        ...

    def delete(self, key: str) -> bool:
        """Evict a specific key from the cache."""
        ...

    def delete_pattern(self, pattern: str) -> int:
        """Evict all keys matching a wildcard pattern."""
        ...

    def invalidate_dashboard_cache(self) -> None:
        """Evict cached executive dashboard metrics and summaries."""
        ...

    def invalidate_customer_cache(self, customer_id: Optional[str] = None) -> None:
        """Evict cached customer list and single customer records."""
        ...

    def invalidate_interaction_cache(self, interaction_id: Optional[str] = None) -> None:
        """Evict cached interaction lists and records."""
        ...

