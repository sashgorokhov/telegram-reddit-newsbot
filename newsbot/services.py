import time

import asyncio

from newsbot import settings, utils, reddit


async def filter_post(post, redis):
    if await redis.exists(post['id']):
        return True
    redis.set(post['id'], time.time(), expire=settings.POST_EXPIRE)


async def gather_posts(subreddits=None):
    subreddits = subreddits or settings.SUBREDDITS

    async with utils.Redis() as redis, reddit.RedditSession() as reddit_session:
        queue = utils.JsonRedisQueue(redis, settings.QUEUE_KEY)
        for subreddit, subreddit_config in subreddits.items():
            async for post in await reddit_session.get_posts(subreddit, **subreddit_config):
                if await filter_post(post, redis):
                    continue
                await queue.put(post)


async def process_queue():
    async with utils.Redis() as redis:
        queue = utils.JsonRedisQueue(redis, settings.QUEUE_KEY)
        post = await queue.get()
    return await process_post(post)


async def process_post(post):
    if post.get('stickied', False):
        return
    domain = post.get('domain', '')
    if 'imgur' in domain:
        return await process_imgur_post(post)
    elif 'reddituploads' in domain or post['url'].endswith('.jpg'):
        return await process_reddit_post(post)
    else:
        return await process_generic_post(post)


async def process_imgur_post(post):
    pass


async def process_reddit_post(post):
    pass


async def process_generic_post(post):
    pass