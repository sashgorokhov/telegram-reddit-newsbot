import uuid

from tests import aiohttp_utils


def create_reddit_response(method, url, *posts):
    data = {
        'data': {
            'children': [i if 'data' in i else {'data': i} for i in posts]
        }
    }
    return aiohttp_utils.create_json_response(method, url, data)


def reddit_post(**kwargs):
    data = {
        'id': str(uuid.uuid4()).split('-')[0],
        'url': 'http://reddit.com/test.jpg',
        'ups': 666,
        'title': 'This is test',
        'author': 'test',
        'permalink': '/r/test',
        'subreddit': '/r/test',
        'domain': 'foo.com'
    }
    data.update(kwargs)
    return data


def imgur_image(**kwargs):
    data = {
        'type': 'image/jpeg',
        'link': 'http://example.com/test.jpg'
    }
    data.update(kwargs)
    return data


async def list_async_gen(async_gen):
    items = list()
    async for item in async_gen:
        items.append(item)
    return items


def make_async_gen(*result, mock=None):
    async def wrapper(*args, **kwargs):
        if mock:
            if result:
                mock(*args, **kwargs)
            else:
                yield mock(*args, **kwargs)
        for r in result:
            yield r

    return wrapper


def make_coro(result=None, mock=None):
    async def wrapper(*args, **kwargs):
        if mock:
            if result:
                mock(*args, **kwargs)
            else:
                return mock(*args, **kwargs)
        if isinstance(result, Exception):
            raise result
        elif not callable(result):
            return result
        else:
            return result(*args, **kwargs)

    return wrapper


def default_reddit_response(session, *posts):
    subreddit = '/r/test'
    charts = ['hot']
    url = session._build_url(subreddit + '/' + charts[0])
    response = create_reddit_response('get', url, *posts)
    return response, subreddit, charts, url
