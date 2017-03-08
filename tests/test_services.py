import json
from unittest import mock

import aioredis
import pytest

from newsbot import services, connections, settings
from newsbot.utils import JsonRedisQueue
from tests import utils


def test_process_generic_post():
    post = utils.reddit_post()
    messages = services.process_generic_post(post)

    assert len(messages) == 2
    assert messages[0]['type'] == 'message'
    assert messages[1]['type'] == 'message'


def test_process_reddit_post():
    post = utils.reddit_post()
    messages = services.process_reddit_post(post)

    assert len(messages) == 2
    assert messages[0]['type'] == 'message'
    assert messages[1]['type'] == 'photo'


@pytest.mark.asyncio
async def test_process_imgur_post_image_jpeg():
    settings.IMGUR_CLIENT_ID = 'Foo'

    post = utils.reddit_post(url='http://imgur.com/test')

    images = [utils.imgur_image()]

    with mock.patch.object(connections.get_imgur_session(), 'get_imgur_images') as patch:
        patch.side_effect = utils.make_async_gen(*images)
        messages = await services.process_imgur_post(post)
        patch.assert_called_with(post['url'])

    assert len(messages) == 2
    assert messages[0]['type'] == 'message'
    assert messages[1]['type'] == 'photo'
    assert messages[1]['params']['photo'] == images[0]['link']


@pytest.mark.asyncio
async def test_process_imgur_post_image_gif():
    settings.IMGUR_CLIENT_ID = 'Foo'

    post = utils.reddit_post(url='http://imgur.com/test')

    images = [utils.imgur_image(type='image/gif')]

    with mock.patch.object(connections.get_imgur_session(), 'get_imgur_images') as patch:
        patch.side_effect = utils.make_async_gen(*images)
        messages = await services.process_imgur_post(post)
        patch.assert_called_with(post['url'])

    assert len(messages) == 2
    assert messages[0]['type'] == 'message'
    assert messages[1]['type'] == 'document'
    assert messages[1]['params']['document'] == images[0]['link']


@pytest.mark.asyncio
async def test_process_imgur_post_image_gif_video():
    settings.IMGUR_CLIENT_ID = 'Foo'

    post = utils.reddit_post(url='http://imgur.com/test')

    images = [utils.imgur_image(type='image/gif', mp4='http://example.com/video.mp4')]

    with mock.patch.object(connections.get_imgur_session(), 'get_imgur_images') as patch:
        patch.side_effect = utils.make_async_gen(*images)
        messages = await services.process_imgur_post(post)
        patch.assert_called_with(post['url'])

    assert len(messages) == 2
    assert messages[0]['type'] == 'message'
    assert messages[1]['type'] == 'video'
    assert messages[1]['params']['video'] == images[0]['mp4']


@pytest.mark.asyncio
async def test_process_imgur_post_image_unknown_type():
    settings.IMGUR_CLIENT_ID = 'Foo'

    post = utils.reddit_post(url='http://imgur.com/test')

    images = [utils.imgur_image(type='image/ktulhu', description='Undescriptible horror')]

    with mock.patch.object(connections.get_imgur_session(), 'get_imgur_images') as patch:
        patch.side_effect = utils.make_async_gen(*images)
        messages = await services.process_imgur_post(post)
        patch.assert_called_with(post['url'])

    assert len(messages) == 2
    assert messages[0]['type'] == 'message'
    assert messages[1]['type'] == 'message'
    assert messages[1]['params']['text'] == images[0]['link']


@pytest.mark.asyncio
async def test_process_post_stickied():
    post = utils.reddit_post(stickied=True)
    messages = await services.process_post(post)
    assert not messages
    assert messages == []


@pytest.mark.asyncio
async def test_process_post_imgur():
    post = utils.reddit_post(domain='imgur.com')

    with mock.patch('newsbot.services.process_imgur_post') as process_imgur_post_mock:
        process_imgur_post_mock.side_effect = utils.make_coro()
        messages = await services.process_post(post)
        process_imgur_post_mock.assert_called_with(post)


@pytest.mark.asyncio
async def test_process_post_reddit():
    post = utils.reddit_post(domain='reddituploads.com')

    with mock.patch('newsbot.services.process_reddit_post') as process_reddit_post_mock:
        messages = await services.process_post(post)
        process_reddit_post_mock.assert_called_with(post)


class MockQueue(JsonRedisQueue):
    def __init__(self, queue=None):
        self.queue = queue or list()
        redis = mock.MagicMock(aioredis.Redis)
        redis.rpush.side_effect = utils.make_coro(result=lambda key, item: self.queue.append(item))
        redis.rpop.side_effect = utils.make_coro(result=lambda key: self.queue.pop())
        redis.lpush.side_effect = utils.make_coro(result=lambda key, item: self.queue.insert(0, item))
        redis.llen.side_effect = utils.make_coro(result=lambda key: len(self.queue))
        super(MockQueue, self).__init__(redis, None)


@pytest.mark.asyncio
async def test_process_post_generic():
    post = utils.reddit_post(domain='gfycat.com', url='http://gfycat.com/test')

    with mock.patch('newsbot.services.process_generic_post') as process_generic_post_mock:
        messages = await services.process_post(post)
        process_generic_post_mock.assert_called_with(post)


@pytest.mark.asyncio
async def test_process_posts():
    posts = [utils.reddit_post()]
    posts_queue = MockQueue(list(map(json.dumps, posts)))
    messages_queue = MockQueue()

    with mock.patch('newsbot.queues.posts_queue') as posts_queue_patch:
        posts_queue_patch.side_effect = utils.make_coro(posts_queue)
        with mock.patch('newsbot.queues.messages_queue') as messages_queue_patch:
            messages_queue_patch.side_effect = utils.make_coro(messages_queue)

            await services.process_posts()

    assert not len(posts_queue.queue)
    assert len(messages_queue.queue)


@pytest.mark.asyncio
async def test_gather_posts(reddit_session):
    posts = [utils.reddit_post()]
    posts_queue = MockQueue()
    settings.SUBREDDITS = {'/r/test': {}}

    with mock.patch('newsbot.queues.posts_queue') as posts_queue_patch:
        posts_queue_patch.side_effect = utils.make_coro(posts_queue)

        with mock.patch.object(reddit_session, 'get_posts') as get_posts_mock:
            get_posts_mock.side_effect = utils.make_async_gen(*posts)

            with mock.patch('newsbot.services.filter_post') as filter_post_mock:
                filter_post_mock.side_effect = utils.make_coro(False)

                with mock.patch('newsbot.connections._reddit_session', new=reddit_session):
                    await services.gather_posts()

    assert len(posts_queue.queue) == len(posts)


@pytest.mark.asyncio
async def test_process_messages():
    post = utils.reddit_post()
    messages = services.process_reddit_post(post)
    messages_queue = MockQueue([json.dumps(messages)])

    telegram_session = connections.get_telegram_session()

    with mock.patch('newsbot.queues.messages_queue') as messages_queue_patch:
        messages_queue_patch.side_effect = utils.make_coro(messages_queue)

        with mock.patch.object(telegram_session, 'process_message') as process_message_mock:
            process_message_mock.side_effect = utils.make_coro({'ok': True})

            await services.process_messages()

    assert not len(messages_queue.queue)
