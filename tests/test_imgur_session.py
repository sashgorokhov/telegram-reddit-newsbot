import asyncio
from unittest import mock

import pytest

from newsbot import connections
from tests import utils, aiohttp_utils


@pytest.fixture
def imgur_session(event_loop):
    async def get_imgur_session():
        return connections.ImgurSession(imgur_client_id='Test')

    async def close_imgur_session(session):
        await session.close()

    session = event_loop.run_until_complete(asyncio.ensure_future(get_imgur_session()))
    try:
        yield session
    finally:
        event_loop.run_until_complete(asyncio.ensure_future(close_imgur_session(session)))


def default_imgur_response(url, *images, **kwargs):
    return aiohttp_utils.create_json_response('get', url, {'success': True, 'data': images, **kwargs})


@pytest.mark.asyncio
async def test_get_imgur_image_unsuccessful(imgur_session):
    response = default_imgur_response('https://api.imgur.com/3/image/test', {'foo': 'bar'}, success=False)

    with aiohttp_utils.mock_session(response, imgur_session) as mocked_session:
        image = await mocked_session.get_imgur_image('test')
        assert image is None


@pytest.mark.asyncio
async def test_get_imgur_image(imgur_session):
    data = {'foo': 'bar'}
    response = default_imgur_response('https://api.imgur.com/3/image/test', data)

    with aiohttp_utils.mock_session(response, imgur_session) as mocked_session:
        image = await mocked_session.get_imgur_image('test')
        assert image[0] == data


@pytest.mark.asyncio
async def test_get_imgur_album_unsuccessful(imgur_session):
    response = default_imgur_response('https://api.imgur.com/3/album/test', {'foo': 'bar'}, success=False)

    with aiohttp_utils.mock_session(response, imgur_session) as mocked_session:
        album = await utils.list_async_gen(mocked_session.get_imgur_album_images('test'))
        assert album == []


@pytest.mark.asyncio
async def test_get_imgur_album(imgur_session):
    data = {'foo': 'bar'}
    response = default_imgur_response('https://api.imgur.com/3/album/test', data={'images': [data]})

    with aiohttp_utils.mock_session(response, imgur_session) as mocked_session:
        album = await utils.list_async_gen(mocked_session.get_imgur_album_images('test'))
        assert album[0] == data


@pytest.mark.asyncio
async def test_get_imgur_images_album(imgur_session):
    url = 'https://imgur.com/a/test'
    imgur_images = [{'foo': 'bar'}]

    with mock.patch.object(imgur_session, 'get_imgur_album_images') as patch:
        patch.side_effect = utils.make_async_gen(*imgur_images)
        images = await utils.list_async_gen(imgur_session.get_imgur_images(url))
        patch.assert_called_with('test')
        assert images == imgur_images


@pytest.mark.asyncio
async def test_get_imgur_images_gallery(imgur_session):
    url = 'https://imgur.com/gallery/test'
    imgur_images = [{'foo': 'bar'}]

    with mock.patch.object(imgur_session, 'get_imgur_album_images') as patch:
        patch.side_effect = utils.make_async_gen(*imgur_images)
        images = await utils.list_async_gen(imgur_session.get_imgur_images(url))
        patch.assert_called_with('test')
        assert images == imgur_images


@pytest.mark.asyncio
async def test_get_imgur_images_image(imgur_session):
    url = 'https://imgur.com/test'
    imgur_images = [{'foo': 'bar'}]

    with mock.patch.object(imgur_session, 'get_imgur_image') as patch:
        patch.side_effect = utils.make_coro(result=imgur_images[0])
        images = await utils.list_async_gen(imgur_session.get_imgur_images(url))

        patch.assert_called_with('test')

        assert images == imgur_images
