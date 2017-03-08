import asyncio
import logging

import pytest

from newsbot import connections

newsbot_logger = logging.getLogger('newsbot')
newsbot_logger.setLevel(logging.NOTSET)
newsbot_logger.propagate = False


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
