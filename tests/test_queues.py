import pytest

from newsbot import queues
from newsbot import settings


@pytest.mark.asyncio
async def test_messages_queue():
    queue = await queues.messages_queue()
    assert queue.key == settings.MESSAGES_QUEUE_KEY


@pytest.mark.asyncio
async def test_posts_queue():
    queue = await queues.posts_queue()
    assert queue.key == settings.POSTS_QUEUE_KEY
