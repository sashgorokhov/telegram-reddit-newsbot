import datetime

SUBREDDITS = dict()

REDIS_URL = 'redis://localhost:6379/0'
TOKEN = None
IMGUR_CLIENT_ID = None

GATHER_POSTS_INTERVAL = datetime.timedelta(minutes=10).total_seconds()
PROCESS_POSTS_INTERVAL = 1
POST_EXPIRE = datetime.timedelta(days=7).total_seconds()

POSTS_QUEUE_KEY = 'posts_queue'
MESSAGES_QUEUE_KEY = 'messages_queue'
