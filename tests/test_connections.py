import pytest

from newsbot import connections
from tests import utils


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


def get_patched_reddit_session(get_mock):
    reddit_session = connections.RedditSession()
    reddit_session.get = get_mock
    return reddit_session


def get_reddit_session(response):
    get_mock = utils.session_get_mock(response)
    return get_patched_reddit_session(get_mock)


@pytest.mark.asyncio
async def test_reddit_session_get_posts():
    post = utils.post()
    response = utils.create_reddit_response(post)

    async with get_reddit_session(response) as reddit_session:
        posts = await utils.list_async_gen(reddit_session.get_posts('/r/test'))

    assert len(posts) == 1
    assert posts[0]['id'] == post['data']['id']


@pytest.mark.asyncio
async def test_reddit_session_get_posts_paginated():
    post = utils.post()
    response = utils.create_reddit_response(post)
    pages = 3

    async with get_reddit_session(response) as reddit_session:
        posts = await utils.list_async_gen(reddit_session.get_posts('/r/test/', pages=pages))

    assert len(posts) == pages
