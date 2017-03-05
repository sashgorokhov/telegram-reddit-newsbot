import pytest

from newsbot import connections


@pytest.mark.asyncio
async def test_redis_connection_creation():
    assert connections._redis is None

    redis = await connections.get_redis()

    assert connections._redis is not None
    assert connections._redis is redis


@pytest.mark.asyncio
async def test_redis_same_connection():
    redis = await connections.get_redis()

    assert await connections.get_redis() is redis
