import asyncio
import time

from newsbot import settings, queues, connections


async def filter_post(post, redis=None):
    redis = redis or await connections.get_redis()
    if await redis.exists(post['id']):
        return True
    await redis.set(post['id'], time.time(), expire=settings.POST_EXPIRE)


async def gather_posts_loop(subreddits=None):
    while True:
        try:
            await gather_posts(subreddits=subreddits)
        finally:
            await asyncio.sleep(settings.GATHER_POSTS_INTERVAL)


async def gather_posts(subreddits=None):
    subreddits = subreddits or settings.SUBREDDITS
    posts_queue = await queues.posts_queue()
    reddit_session = connections.get_reddit_session()

    for subreddit, subreddit_config in subreddits.items():
        # noinspection PyTypeChecker
        async for post in reddit_session.get_posts(subreddit, **subreddit_config):
            if await filter_post(post):
                continue
            await posts_queue.put(post)


async def process_posts_queue_loop():
    while True:
        try:
            await process_posts()
        finally:
            await asyncio.sleep(settings.PROCESS_POSTS_INTERVAL)


async def process_posts():
    posts_queue = await queues.posts_queue()
    messages_queue = await queues.messages_queue()

    if await posts_queue.empty():
        return

    post = await posts_queue.get()

    if post:
        messages = await process_post(post)
        if not messages:
            return
        await messages_queue.put(messages)


async def process_post(post):
    if post.get('stickied', False):
        return
    domain = post.get('domain', '')
    if 'imgur' in domain:
        return await process_imgur_post(post)
    elif 'reddituploads' in domain or post['url'].endswith('.jpg'):
        return process_reddit_post(post)
    else:
        return process_generic_post(post)


async def process_imgur_post(post):
    imgur_session = connections.get_imgur_session()
    text = get_caption(post) + '\n' + post['url']

    messages = [
        {'type': 'message', 'params': {
            'text': text, 'disable_web_page_preview': True, 'parse_mode': 'HTML'}},
    ]

    # noinspection PyTypeChecker
    async for image in imgur_session.get_imgur_images(post['url']):
        kwargs = {}
        if image.get('description', None):
            kwargs['caption'] = image['description'][:200]
        if image['type'] == 'image/jpeg':
            messages.append({'type': 'photo', 'params': {'photo': image['link'], **kwargs}})
        elif image['type'] == 'image/gif':
            if 'mp4' in image:
                messages.append({'type': 'video', 'params': {'video': image['mp4'], **kwargs}})
            else:
                messages.append({'type': 'document', 'params': {'document': image['link'], **kwargs}})
        else:
            messages.append({'type': 'message', 'params': {'text': image['link'], **kwargs}})

    return messages


def process_reddit_post(post):
    post['url'] = post['url'].replace('amp;', '')
    text = get_caption(post)

    messages = [
        {'type': 'message', 'params': {'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': True}},
        {'type': 'photo', 'params': {'photo': post['url']}}
    ]

    return messages


def process_generic_post(post):
    post['url'] = post['url'].replace('amp;', '')
    text = get_caption(post)

    messages = [
        {'type': 'message', 'params': {'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': True}},
        {'type': 'message', 'params': {'text': post['url']}}
    ]

    return messages


def get_caption(post):
    template = "/r/{0[subreddit]} - <a href=\"https://www.reddit.com/u/{0[author]}\">{0[author]}</a>" \
               ": {0[title]} ({1} {0[ups]}, <a href=\"https://www.reddit.com{0[permalink]}\">comments</a>)"
    return template.format(post, chr(int('2191', 16)))  # arrow up
