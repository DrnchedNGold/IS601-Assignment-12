import pytest
from unittest.mock import patch, MagicMock
from app.auth import redis as redis_module

def test_get_redis_first_time(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr(redis_module.redis, "Redis", MagicMock(from_url=MagicMock(return_value=mock_redis)))
    # Remove cached attribute if present
    if hasattr(redis_module.get_redis, "redis"):
        delattr(redis_module.get_redis, "redis")
    result = redis_module.get_redis()
    assert result is mock_redis

def test_get_redis_cached(monkeypatch):
    mock_redis = MagicMock()
    redis_module.get_redis.redis = mock_redis
    result = redis_module.get_redis()
    assert result is mock_redis

def test_add_to_blacklist(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr(redis_module, "get_redis", MagicMock(return_value=mock_redis))
    redis_module.add_to_blacklist("testjti", 10)
    mock_redis.set.assert_called_with("blacklist:testjti", "1", ex=10)

def test_is_blacklisted(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.get.return_value = b"1"
    monkeypatch.setattr(redis_module, "get_redis", MagicMock(return_value=mock_redis))
    def is_blacklisted(jti: str) -> bool:
        redis_conn = redis_module.get_redis()
        return redis_conn.get(f"blacklist:{jti}") == b"1"
    monkeypatch.setattr(redis_module, "is_blacklisted", is_blacklisted)
    assert redis_module.is_blacklisted("testjti") is True
    mock_redis.get.return_value = None
    assert redis_module.is_blacklisted("testjti") is False
