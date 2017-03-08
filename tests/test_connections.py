import pytest

from newsbot import connections
from newsbot import settings


@pytest.mark.asyncio
async def test_redis_same_connection():
    redis = await connections.get_redis()

    assert await connections.get_redis() is redis


@pytest.mark.asyncio
async def test_reddit_same_session():
    session = connections.get_reddit_session()
    assert connections.get_reddit_session() is session


@pytest.mark.asyncio
async def test_telegram_same_session():
    session = connections.get_telegram_session()
    assert connections.get_telegram_session() is session


@pytest.mark.asyncio
async def test_imgur_same_session():
    settings.IMGUR_CLIENT_ID = ''
    session = connections.get_imgur_session()
    assert connections.get_imgur_session() is session
