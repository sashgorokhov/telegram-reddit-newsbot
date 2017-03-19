import os

import metayaml

CONFIG = None


def read_config(filename=None):
    filename = filename or os.environ.get('NEWSBOT_CONFIG',
                                          os.path.join(os.path.dirname(os.path.dirname(__file__)), 'newsbot.yaml'))
    return metayaml.read(filename, disable_order_dict=True, defaults={'env': os.environ})


def configure_logging():
    import logging

    logger = logging.getLogger('newsbot')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(name)s:%(funcName)s] [%(levelname)s] %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    logger.addHandler(stream_handler)


configure_logging()

del configure_logging

USER_AGENT = 'Python reddit newsbot'
POSTS_QUEUE_KEY = 'posts_queue'
MESSAGES_QUEUE_KEY = 'messages_queue'
