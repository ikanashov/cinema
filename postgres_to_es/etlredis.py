from logging import log
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

import redis

from loguru import logger


class ETLRedis:
    def __init__(self, envfile='../.env'):
        dotenv_path = os.path.join(os.path.dirname(__file__), envfile)
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

        self.prefix = os.getenv('REDIS_PREFIX', '') + ':'
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', '127.0.0.1'),
            port=os.getenv('REDIS_PORT', '6379'),
            password=os.getenv('REDIS_PASSWORD', ''),
        )

    def get_key(self, key: str) -> str:
        return self.prefix + key

    def ping(self):
        logger.debug(self.redis.ping())

    def test(self):
        self.redis.set(self.get_key('test'), 'test1')
        logger.debug(self.redis.get(self.get_key('test')))

if __name__ == '__main__':
    z = ETLRedis()
    z.ping()
    z.test()
    