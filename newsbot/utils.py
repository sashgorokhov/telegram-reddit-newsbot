import json
from urllib import parse

import aioredis
from aiocontext import async_contextmanager


class StopScheduler(Exception):
    pass


class RedisQueue(object):
    def __init__(self, redis, key):
        """
        :param aioredis.Redis redis:
        """
        super(RedisQueue, self).__init__()
        self.redis = redis
        self.key = key

    async def get(self):
        data = await self.redis.rpop(self.key)
        return self._decode(data)

    async def insert(self, item):
        data = self._encode(item)
        return await self.redis.rpush(self.key, data)

    async def put(self, item):
        data = self._encode(item)
        return await self.redis.lpush(self.key, data)

    async def items(self):
        for item in await self.redis.lrange(self.key, 0, -1):
            yield self._decode(item)

    def _encode(self, data):
        raise data

    def _decode(self, data):
        raise data

    async def size(self):
        return await self.redis.llen(self.key)

    async def empty(self):
        return await self.size() == 0

    async def clear(self):
        return await self.redis.delete(self.key)


class JsonRedisQueue(RedisQueue):
    def _encode(self, data):
        return json.dumps(data)

    def _decode(self, data):
        return json.loads(data)


@async_contextmanager
async def maybe(obj, func, *args, **kwargs):
    if obj is None:
        async with func(*args, **kwargs) as obj:
            yield obj
    else:
        yield obj


def parse_redis_url(redis_url):  # pragma: no cover
    """
    redis.connection.ConnectionPool#from_url
    """
    url_string = redis_url
    url = parse.urlparse(redis_url)

    if '?' in url.path and not url.query:
        qs = url.path.split('?', 1)[1]
        url = parse.urlparse(url_string[:-(len(qs) + 1)])
    else:
        qs = url.query

    url_options = {}

    for name, value in parse.parse_qs(qs).items():
        if value and len(value) > 0:
            url_options[name] = value[0]

    password = url.password
    path = url.path
    hostname = url.hostname

    if url.scheme == 'unix':
        url_options.update({
            'password': password,
            'path': path
        })

    else:
        url_options.update({
            'host': hostname,
            'port': int(url.port or 6379),
            'password': password,
        })

        if 'db' not in url_options and path:
            try:
                url_options['db'] = int(path.replace('/', ''))
            except (AttributeError, ValueError):
                pass

    url_options['db'] = int(url_options.get('db', 0))
    return url_options
