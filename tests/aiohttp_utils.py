import asyncio
import contextlib
import json
from unittest import mock

import aiohttp
from yarl import URL


def create_response(method, url, content, loop=None):
    loop = loop or asyncio.get_event_loop()

    response = aiohttp.ClientResponse(method.lower(), URL(url))

    def side_effect(*args, **kwargs):
        fut = loop.create_future()
        if isinstance(content, str):
            fut.set_result(content.encode())
        else:
            fut.set_result(content)
        return fut

    response.content = mock.Mock()
    response.content.read.side_effect = side_effect

    return response


def create_json_response(method, url, data, loop=None):
    json_data = json.dumps(data)
    response = create_response(method, url, json_data, loop=loop)
    response.headers = response.headers or dict()
    response.headers['Content-Type'] = 'application/json'
    return response


@contextlib.contextmanager
def mock_session(response, session=None, mock_object=None):
    """
    :param aiohttp.ClientSession session:
    :param aiohttp.ClientResponse|list[aiohttp.ClientResponse] response:
    """
    session = session or aiohttp.ClientSession()
    request = session._request

    session.mock = mock_object or mock.Mock()
    if isinstance(response, (list, tuple)):
        session.mock.side_effect = response
    else:
        session.mock.return_value = response

    async def _request(*args, **kwargs):
        return session.mock(*args, **kwargs)

    try:
        with mock.patch.object(session, '_request') as request_mock:
            request_mock.side_effect = _request
            yield session
    finally:
        delattr(session, 'mock')
