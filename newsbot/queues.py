from newsbot import settings, connections
from newsbot.utils import JsonRedisQueue


async def posts_queue():
    redis = await connections.get_redis()
    return JsonRedisQueue(redis, settings.POSTS_QUEUE_KEY)


async def messages_queue():
    redis = await connections.get_redis()
    return JsonRedisQueue(redis, settings.MESSAGES_QUEUE_KEY)
