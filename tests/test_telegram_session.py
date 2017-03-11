import pytest

from newsbot import connections
from tests import aiohttp_utils


@pytest.mark.asyncio
async def test_too_many_requests(telegram_session):
    response = aiohttp_utils.create_json_response('post', 'http://example.com/test', {
        'ok': False, 'error_code': 429, 'parameters': {'retry_after': 10}
    })
    response.status = 429

    with pytest.raises(connections.TelegramTooManyRequests) as e:
        with aiohttp_utils.mock_session(response, telegram_session) as session:
            await session.send('sendMessage', {'hello': 'world!'})
    assert e.value.code == 429
    assert e.value.retry_after == 10
