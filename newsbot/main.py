import asyncio
import os


def main(noserver=False):  # pragma: no cover
    import argparse
    from newsbot import settings

    parser = argparse.ArgumentParser('newsbot')
    parser.add_argument('--noserver', default=False, action='store_true')
    parser.add_argument('--redis_url', default=os.environ.get('NEWSBOT_REDIS_URL', 'redis://localhost:6379/0'))
    parser.add_argument('--token', default=os.environ.get('NEWSBOT_TOKEN', None))
    parser.add_argument('--chat_id', default=os.environ.get('NEWSBOT_CHAT_ID', None))
    parser.add_argument('--imgur_client_id', default=os.environ.get('NEWSBOT_IMGUR_CLIENT_ID', None))
    parser.add_argument('--subreddit', nargs=1)

    kwargs = vars(parser.parse_args())
    for key, value in kwargs.items():
        if not hasattr(settings, key.upper()):
            continue
        if value is None:
            parser.error(key + ' is not set')
        else:
            setattr(settings, key.upper(), value)

    settings.SUBREDDITS = {i: {'charts': ['hot', 'top']} for i in kwargs['subreddit']}

    noserver = kwargs.get('noserver', noserver)

    from newsbot import server, services

    loop = asyncio.get_event_loop()

    def exception_handler(loop, context):
        d = dict()
        for key, value in context.items():
            try:
                d[key] = str(value)
            except AssertionError:
                d[key] = 'Error!'
        print(d)

    loop.set_exception_handler(exception_handler)

    loop.create_task(services.gather_posts())
    loop.create_task(services.process_posts_queue_loop())
    loop.create_task(services.process_messages_loop())

    if noserver:
        return loop.run_forever()
    else:
        return server.run_server(loop=loop)

if __name__ == '__main__':
    main()