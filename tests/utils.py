import asyncio
import json
import uuid
from unittest import mock

import aiohttp
from aiocontext import async_contextmanager
from aiohttp import helpers
from yarl import URL


def create_response(data):
    response = aiohttp.ClientResponse('get', URL('http://reddit.com/.json'))
    response.headers = {'Content-Type': 'application/json'}

    def side_effect(*args, **kwargs):
        fut = helpers.create_future(asyncio.get_event_loop())
        fut.set_result(json.dumps(data).encode())
        return fut

    content = response.content = mock.Mock()
    content.read.side_effect = side_effect

    return response


def create_reddit_response(*posts):
    data = {
        'data': {
            'children': posts
        }
    }
    return create_response(data)


def session_get_mock(response):
    # get_mock = mock.Mock()

    @async_contextmanager
    async def get_response(*args, **kwargs):
        yield response

    # get_mock.return_value = get_response
    # return get_mock
    return get_response


def post(**kwargs):
    data = {
        'data': {
            'id': str(uuid.uuid4()).split('-')[0]
        }
    }
    data.update(kwargs)
    return data


async def list_async_gen(async_gen):
    items = list()
    async for item in async_gen:
        items.append(item)
    return items
