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
        self.queuename = self.prefix + 'filmids'
        self.workqueuename = self.queuename + ':work'

        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', '127.0.0.1'),
            port=os.getenv('REDIS_PORT', '6379'),
            password=os.getenv('REDIS_PASSWORD', ''),
            decode_responses=True,
        )

    def get_key(self, key: str) -> str:
        return self.prefix + key
    
    def set_status(self, status: str) -> str:
        key = self.prefix + 'status'
        self.redis.set(key, status)
        return self.redis.get(key)

    def get_status(self) -> str:
        key = self.prefix + 'status'
        return self.redis.get(key)

    def set_lasttime(self, table: str, lasttime: datetime) -> datetime:
        key = self.prefix + table + ':lasttime'
        self.redis.set(key, lasttime.isoformat())
        time = self.redis.get(key)
        return datetime.fromisoformat(time)

    def get_lasttime(self, table: str) -> datetime:
        key = self.prefix + table + ':lasttime'
        try:
            time = self.redis.get(key)
            return time
        except redis.ConnectionError as err:
            logger.debug(err)
            raise NameError('redis not answer')

    def push_filmid(self, id: str) -> str:
        script = f'redis.call("LREM",KEYS[1], "0", ARGV[1]);'
        script += f'return redis.call("LPUSH", KEYS[1], ARGV[1])'
        self.redis.eval(script, 1, self.queuename, id)

    def get_filmid_for_work(self, size) -> list:
        size -= self.redis.llen(self.workqueuename)
        while size > 0:
            self.redis.rpoplpush(self.queuename, self.workqueuename)
            size -=1
        len = self.redis.llen(self.workqueuename)
        workid = self.redis.lrange(self.workqueuename, 0, len)
        return workid
    
    def del_work_queuename(self):
        self.redis.delete(self.workqueuename)
    
    #remove
    def ping(self):
        logger.debug(self.redis.ping())
    
    #remove
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
    
    