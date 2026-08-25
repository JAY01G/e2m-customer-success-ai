import pytest
from app.services.cache_service import CacheService


def test_cache_service_graceful_degradation_when_disabled():
    service = CacheService()
    service.enabled = False
    service._client = None

    # Operations must not throw errors
    assert service.get("any_key") is None
    assert service.set("any_key", {"test": 123}) is False
    assert service.delete("any_key") is False
    assert service.delete_pattern("pattern:*") == 0
    assert service.is_healthy() is False

    # Invalidation helpers must run safely without raising exceptions
    service.invalidate_customer_cache("cust-123")
    service.invalidate_interaction_cache("inter-123")
    service.invalidate_dashboard_cache()


def test_cache_service_fallback_on_client_exception():
    service = CacheService()
    service.enabled = True

    class BrokenRedis:
        def get(self, key):
            raise ConnectionError("Redis server connection refused")

        def setex(self, key, time, value):
            raise ConnectionError("Redis server connection refused")

        def delete(self, *keys):
            raise ConnectionError("Redis server connection refused")

        def ping(self):
            raise ConnectionError("Redis server connection refused")

    service._client = BrokenRedis()

    # Graceful fallback returns None instead of raising unhandled 500 exception
    assert service.get("customers:list:1") is None
    assert service.set("customers:list:1", {"data": "test"}) is False
    assert service.is_healthy() is False
