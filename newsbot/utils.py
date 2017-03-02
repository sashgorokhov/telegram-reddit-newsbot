import asyncio
import datetime
import json
import aioredis

from newsbot import settings


async def scheduler(tasks, period=datetime.timedelta(minutes=1)):
    if not isinstance(period, datetime.timedelta):
        if isinstance(period, int):
            period = datetime.timedelta(seconds=period)
        else:
            raise TypeError('period must be either int or datetime.timedelta, not %s' % type(period))

    while True:
        await asyncio.sleep(period.total_seconds())
        for task in tasks:
             await task()


class RedisQueue(asyncio.Queue):
    def __init__(self, redis, key):
        """
        :param aioredis.Redis redis:
        """
        super(RedisQueue, self).__init__()
        self.redis = redis
        self.key = key

    def _init(self, maxsize):
        pass

    def _get(self):
        data = self.redis.rpop(self.key)
        return self._decode(data)

    def _put(self, item):
        data = self._encode(item)
        return self.redis.lpush(self.key, data)

    def _encode(self, data):
        raise NotImplementedError

    def _decode(self, data):
        raise NotImplementedError

    def _qsize(self):
        return self.redis.llen(self.key)


class JsonRedisQueue(RedisQueue):
    def _encode(self, data):
        return json.dumps(data)

    def _decode(self, data):
        return json.loads(data)


class Redis(aioredis.Redis):
    def __init__(self, address=None):
        self.address = address or settings.REDIS_URL
        super(Redis, self).__init__(None)

    async def __aenter__(self):
        self._conn = await aioredis.create_connection(self.address)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
