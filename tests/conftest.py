import asyncio

import pytest

from newsbot import connections


@pytest.fixture
def reddit_session(event_loop):
    async def get_reddit_session():
        return connections.RedditSession()

    async def close_reddit_session(session):
        await session.close()

    session = event_loop.run_until_complete(asyncio.ensure_future(get_reddit_session()))
    try:
        yield session
    finally:
        event_loop.run_until_complete(asyncio.ensure_future(close_reddit_session(session)))


@pytest.fixture
def imgur_session(event_loop):
    async def get_imgur_session():
        return connections.ImgurSession(imgur_client_id='Test')

    async def close_imgur_session(session):
        await session.close()

    session = event_loop.run_until_complete(asyncio.ensure_future(get_imgur_session()))
    try:
        yield session
    finally:
        event_loop.run_until_complete(asyncio.ensure_future(close_imgur_session(session)))


@pytest.fixture
def telegram_session(event_loop):
    async def get_telegram_session():
        return connections.TelegramSession(token='test', chat_id='test')

    async def close_telegram_session(session):
        await session.close()

    session = event_loop.run_until_complete(asyncio.ensure_future(get_telegram_session()))
    try:
        yield session
    finally:
        event_loop.run_until_complete(asyncio.ensure_future(close_telegram_session(session)))
