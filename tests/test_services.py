from unittest import mock

import pytest

from newsbot import services, connections, settings
from tests import utils


def test_process_generic_post():
    post = utils.post()['data']
    messages = services.process_generic_post(post)

    assert len(messages) == 2
    assert messages[0]['type'] == 'message'
    assert messages[1]['type'] == 'message'


def test_process_reddit_post():
    post = utils.post()['data']
    messages = services.process_reddit_post(post)

    assert len(messages) == 2
    assert messages[0]['type'] == 'message'
    assert messages[1]['type'] == 'photo'


@pytest.mark.asyncio
async def test_process_imgur_post():
    settings.IMGUR_CLIENT_ID = 'Foo'

    post = utils.post(url='http://imgur.com/a/test')['data']

    images = [utils.imgur_image()]
    response = utils.create_response({'success': True, 'data': {'images': images}})

    imgur_session = connections.get_imgur_session()
    imgur_session.get = utils.session_get_mock(response)

    messages = await services.process_imgur_post(post)

    assert len(messages) == 2
    assert messages[0]['type'] == 'message'
    assert messages[1]['type'] == 'photo'


@pytest.mark.asyncio
async def test_process_post_imgur():
    with mock.patch('newsbot.services.process_imgur_post') as process_imgur_post_mock:
        post = utils.post(url='http://imgur.com/a/test', domain='imgur.com')['data']
        await services.process_post(post)
        assert process_imgur_post_mock.called
