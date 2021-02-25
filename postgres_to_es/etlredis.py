from logging import log
import os
from datetime import date, datetime, timezone
import random

from dotenv import load_dotenv

import redis

from loguru import logger

from etldecorator import backoff

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

    @backoff(0.0001)
    def set_status(self, service: str, status: str) -> str:
        key = self.prefix + 'status:'+ service
        self.redis.set(key, status)
        return self.redis.get(key)
    
    @backoff(0.0001)
    def get_status(self, service: str) -> str:
        key = self.prefix + 'status:'+ service
        return self.redis.get(key)

    @backoff(0.0001)
    def set_lasttime(self, table: str, lasttime: datetime) -> datetime:
        key = self.prefix + table + ':lasttime'
        self.redis.set(key, lasttime.isoformat())
        time = self.redis.get(key)
        return datetime.fromisoformat(time)

    @backoff(0.0001)
    def get_lasttime(self, table: str) -> datetime:
        key = self.prefix + table + ':lasttime'
        try:
            time = self.redis.get(key)
            return time
        except redis.ConnectionError as err:
            logger.debug(err)
            raise NameError('redis not answer')
    
    @backoff(0.0001)
    def push_filmid(self, id: str) -> str:
        script = f'redis.call("LREM",KEYS[1], "0", ARGV[1]);'
        script += f'return redis.call("LPUSH", KEYS[1], ARGV[1])'
        self.redis.eval(script, 1, self.queuename, id)

    @backoff(0.0001)
    def get_filmid_for_work(self, size) -> list:
        size -= self.redis.llen(self.workqueuename)
        logger.debug(size)
        logger.debug(self.redis.llen(self.workqueuename))
        while size > 0:
            self.redis.rpoplpush(self.queuename, self.workqueuename)
            size -=1
        len = self.redis.llen(self.workqueuename)
        workid = self.redis.lrange(self.workqueuename, 0, len)
        logger.debug(workid)
        return workid
    
    @backoff(0.0001)
    def del_work_queuename(self):
        self.redis.delete(self.workqueuename)

if __name__ == '__main__':
    z = ETLRedis()    
    while True:
        z.set_status('consumer', str(random.uniform(1,10)))
        logger.debug(z.get_status('consumer'))