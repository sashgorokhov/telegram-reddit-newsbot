import datetime


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

SUBREDDITS = dict()

REDIS_URL = 'redis://localhost:6379/0'
TOKEN = None
IMGUR_CLIENT_ID = None
CHAT_ID = None

USER_AGENT = 'Python reddit newsbot'
GATHER_POSTS_INTERVAL = round(datetime.timedelta(minutes=10).total_seconds())
PROCESS_POSTS_INTERVAL = 1
PROCESS_MESSAGES_INTERVAL = 1
POST_EXPIRE = round(datetime.timedelta(days=7).total_seconds())

POSTS_QUEUE_KEY = 'posts_queue'
MESSAGES_QUEUE_KEY = 'messages_queue'
