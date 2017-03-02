import datetime

SUBREDDITS = dict()

REDIS_URL = None
TOKEN = None

POST_EXPIRE = datetime.timedelta(days=7).total_seconds()

QUEUE_KEY = 'posts_queue'