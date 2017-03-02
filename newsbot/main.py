import asyncio
import os
from datetime import timedelta


def main():
    import argparse
    from newsbot import settings

    parser = argparse.ArgumentParser('newsbot')
    parser.add_argument('--redis_url', default=os.environ.get('NEWSBOT_REDIS_URL', None))
    parser.add_argument('--token', default=os.environ.get('NEWSBOT_TOKEN', None))
    parser.add_argument('--imgur_client_id', default=os.environ.get('NEWSBOT_IMGUR_CLIENT_ID', None))

    kwargs = vars(parser.parse_args())
    for key, value in kwargs.items():
        if value is None:
            parser.error(key + ' is not set')
        else:
            setattr(settings, key.upper(), value)

    from newsbot import server, utils, services

    loop = asyncio.get_event_loop()
    loop.create_task(utils.scheduler([services.gather_posts], period=timedelta(minutes=10)))
    loop.create_task(utils.scheduler([services.process_queue], period=timedelta(seconds=1)))

    return server.run_server(loop=loop)

if __name__ == '__main__':
    main()