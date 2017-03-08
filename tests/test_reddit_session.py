from unittest import mock

import pytest

from tests import aiohttp_utils
from tests import utils


@pytest.mark.asyncio
async def test_useragent_header_set(reddit_session):
    assert 'User-Agent' in reddit_session._default_headers
    assert reddit_session._default_headers.get('User-Agent')


@pytest.mark.asyncio
async def test_get_posts_no_posts(reddit_session):
    response, subreddit, charts, url = utils.default_reddit_response(reddit_session)

    with aiohttp_utils.mock_session(response, reddit_session) as mocked_session:
        posts = await utils.list_async_gen(mocked_session.get_posts(subreddit, charts=charts))
        assert len(posts) == 0
        assert mocked_session.mock.call_args == mock.call('GET', url, allow_redirects=True)


@pytest.mark.asyncio
async def test_empty_post(reddit_session):
    response, subreddit, charts, url = utils.default_reddit_response(reddit_session, {})

    with aiohttp_utils.mock_session(response, reddit_session) as mocked_session:
        posts = await utils.list_async_gen(mocked_session.get_posts(subreddit, charts=charts))
        assert len(posts) == 0


@pytest.mark.asyncio
async def test_pagination(reddit_session):
    page1_posts = [utils.reddit_post()]
    page2_posts = [utils.reddit_post()]
    page1_response, subreddit, charts, url = utils.default_reddit_response(reddit_session, *page1_posts)
    page2_response, _, _, _ = utils.default_reddit_response(reddit_session, *page2_posts)

    with aiohttp_utils.mock_session([page1_response, page2_response], reddit_session) as mocked_session:
        reddit_posts = await utils.list_async_gen(mocked_session.get_posts(subreddit, charts=charts, pages=2))
        assert len(reddit_posts) == len(page1_posts + page2_posts)
        assert reddit_posts[0] == page1_posts[0]
        assert reddit_posts[1] == page2_posts[0]

        assert reddit_session.mock.call_args_list[1] == \
               mock.call('GET', url, allow_redirects=True, params={'after': page1_posts[-1]['id']})
