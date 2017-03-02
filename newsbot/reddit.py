import aiohttp


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

        if page > pages:
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
