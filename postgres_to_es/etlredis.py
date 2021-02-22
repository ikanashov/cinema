from logging import log
import os
from datetime import date, datetime, timezone

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
            decode_responses=True,
        )

    def get_key(self, key: str) -> str:
        return self.prefix + key
    
    def set_lasttime(self, table: str, lasttime: datetime) -> datetime:
        key = self.prefix + table + ':lasttime'
        self.redis.set(key, lasttime.isoformat())
        time = self.redis.get(key)
        return datetime.fromisoformat(time)

    def get_lasttime(self, table: str) -> datetime:
        key = self.prefix + table + ':lasttime'
        time = self.redis.get(key)
        return time

    def push_filmid(self, id: str) -> str:
        queuename = self.prefix + 'filmids'
        script = f'redis.call("LREM",KEYS[1], "0", ARGV[1]);'
        script += f'return redis.call("LPUSH", KEYS[1], ARGV[1])'
        self.redis.eval(script, 1, queuename, id)

    def ping(self):
        logger.debug(self.redis.ping())

    def test(self):
        self.redis.set(self.get_key('test'), 'test1')
        logger.debug(self.redis.get(self.get_key('test')))

if __name__ == '__main__':
    lasttime = datetime.fromisoformat('2021-01-24 17:00:56.990682+00:00')
    logger.debug(lasttime)
    z = ETLRedis()
    #time = z.set_lasttime('test', lasttime)
    time = z.get_lasttime('test1')
    logger.debug(time)
    
    