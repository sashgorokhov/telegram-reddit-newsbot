import asyncio
import os


def main(noserver=False):  # pragma: no cover
    import argparse
    from newsbot import settings

    parser = argparse.ArgumentParser('newsbot')
    parser.add_argument('--noserver', default=False, action='store_true')
    parser.add_argument('--config', default=None)
    parser.add_argument('--redis_url', default=None)

    kwargs = vars(parser.parse_args())
    settings.CONFIG = settings.read_config(kwargs.get('config', None))
    settings.CONFIG['redis'] = os.environ.get('REDIS_URL', kwargs.get('redis_url', None) or settings.CONFIG['redis'])

    noserver = kwargs.get('noserver', noserver)

    from newsbot import server, services

    loop = asyncio.get_event_loop()

    loop.create_task(services.gather_posts())
    loop.create_task(services.process_posts_queue_loop())
    loop.create_task(services.process_messages_loop())

    if noserver:
        return loop.run_forever()
    else:
        return server.run_server(loop=loop)

if __name__ == '__main__':
    main()