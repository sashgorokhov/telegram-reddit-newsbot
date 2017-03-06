import os
import urllib.parse

import aiohttp
import aioredis

from newsbot import settings, utils

_redis = None
_reddit_session = None
_imgur_session = None


async def get_redis(address=settings.REDIS_URL, loop=None, recreate=False) -> aioredis.Redis:
    global _redis
    kwargs = utils.parse_redis_url(address)
    kwargs['address'] = kwargs.pop('host'), kwargs.pop('port')
    if not _redis or recreate:
        _redis = await aioredis.create_reconnecting_redis(loop=loop, **kwargs)
    return _redis


class RedditSession(aiohttp.ClientSession):
    user_agent = 'Python reddit newsbot (by /u/sashgorokhov)'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('headers', dict())
        kwargs['headers'].setdefault('User-Agent', self.user_agent)
        super(RedditSession, self).__init__(*args, **kwargs)

    def build_url(self, subreddit):
        return 'https://www.reddit.com%s.json' % subreddit

    async def _get_posts(self, subreddit, pages=1, **kwargs):
        page = kwargs.pop('page', 1)
        url = self.build_url(subreddit)
        post = None

        async with self.get(url, **kwargs) as response:
            json_body = await response.json()

        for post in json_body.get('data', {}).get('children', []):
            post = post.get('data', {})
            if not post:
                continue
            yield post

        if page >= pages:
            return
        elif post:
            kwargs.setdefault('params', dict())
            kwargs['params']['after'] = post['id']
            kwargs['page'] = page + 1
            async for post in self._get_posts(subreddit, pages=pages, **kwargs):
                yield post

    async def get_posts(self, subreddit, charts=None, pages=1, **kwargs):
        charts = charts or ['hot']
        for chart in charts:
            subreddit_chart = subreddit
            if not subreddit_chart.endswith('/'):
                subreddit_chart += '/'
            subreddit_chart += chart
            async for post in self._get_posts(subreddit_chart, pages=pages, **kwargs):
                yield post


class ImgurSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        imgur_client_id = kwargs.pop('imgur_client_id', settings.IMGUR_CLIENT_ID)
        kwargs.setdefault('headers', dict())
        kwargs['headers'].setdefault('Authorization', 'Client-ID ' + imgur_client_id)
        super(ImgurSession, self).__init__(*args, **kwargs)

    async def get_imgur_images(self, imgur_url):
        split_result = urllib.parse.urlsplit(imgur_url)
        if split_result.path.startswith('/a/') or split_result.path.startswith('/gallery/'):
            album_id = split_result.path.split('/')[-1]
            async for image in self.get_imgur_album_images(album_id):
                yield image
        else:
            image_id = os.path.splitext(split_result.path[1:])[0]
            image = await self.get_imgur_image(image_id)
            if image:
                yield image

    async def get_imgur_image(self, image_id):
        async with self.get('https://api.imgur.com/3/image/' + image_id) as response:
            image = await response.json()
        if not image.get('success', False):
            return
        return image.get('data', None)

    async def get_imgur_album_images(self, album_id):
        async with self.get('https://api.imgur.com/3/album/' + album_id) as response:
            album = await response.json()
        if not album.get('success', False):
            return
        for image in album.get('data', {}).get('images', []):
            yield image


def get_reddit_session() -> RedditSession:
    global _reddit_session
    if not _reddit_session:
        _reddit_session = RedditSession()
    return _reddit_session


def get_imgur_session() -> ImgurSession:
    global _imgur_session
    if not _imgur_session:
        _imgur_session = ImgurSession()
    return _imgur_session
