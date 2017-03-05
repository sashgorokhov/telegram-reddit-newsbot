import pytest
from aiocontext import async_contextmanager

from newsbot import connections, utils

redis_tests_key = 'tests'


@async_contextmanager
async def json_queue():
    redis = await connections.get_redis(recreate=True)
    await redis.delete(redis_tests_key)
    try:
        yield utils.JsonRedisQueue(redis, redis_tests_key)
    finally:
        await redis.delete(redis_tests_key)


@pytest.mark.asyncio
async def test_json_queue():
    async with json_queue() as queue:
        message = {'msg': 'Foo'}
        await queue.put(message)
        assert await queue.get() == message


@pytest.mark.asyncio
async def test_json_queue_length():
    async with json_queue() as queue:
        assert await queue.size() == 0
        await queue.put({'m': 'Foo'})
        assert await queue.size() == 1
        await queue.get()
        assert await queue.size() == 0


@pytest.mark.asyncio
async def test_json_queue_empty():
    async with json_queue() as queue:
        assert await queue.size() == 0
        assert await queue.empty()
