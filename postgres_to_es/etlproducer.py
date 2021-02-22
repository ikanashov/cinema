from logging import debug, log
import os
from datetime import date, datetime, timezone

from dotenv import load_dotenv

from loguru import logger

if __name__ == '__main__':
    from etlredis import ETLRedis
    from etlpostgres import ETLPG
else:
    from .etlredis import ETLRedis
    from .etlpostgres import ETLPG

class ETLProducer:
    producer_table = [
        'djfilmwork',
        'djfilmperson',
        'djfilmgenre',
        'djfilmtype',
    ]

    def __init__(self, envfile='../.env'):
        dotenv_path = os.path.join(os.path.dirname(__file__), envfile)
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        self.limit = int(os.getenv('ETL_SIZE_LIMIT', '7'))

        self.redis = ETLRedis()
        self.pgbase = ETLPG()

    def producer(self, table: str) -> list:
        lasttime = self.redis.get_lasttime(table) or self.pgbase.get_first_object_time(table)
        idlists = self.pgbase.get_updated_object_id(lasttime, table, self.limit)
        try:
            lasttime = idlists[-1].modified
            lasttime = self.redis.set_lasttime(table, idlists[-1].modified)
        except IndexError:
            logger.debug(f'No more new data in {table}')
        idlists = [filmid.id for filmid in idlists]
        return idlists
    
    def enricher(self, table: str, idlists: list) -> list:
        offset = 0
        isupdatedid = True if len(idlists) > 0 else False
        while isupdatedid:
            filmids = self.pgbase.get_filmgenreupdated_id(tuple(idlists), self.limit, offset)
            for id in filmids:
                self.redis.push_filmid(id[0])
            if len(filmids) == self.limit:
                offset += self.limit
            else:
                isupdatedid = False

if __name__ == '__main__':
    z = ETLProducer()
    idlists = z.producer('djfilmgenre')
    logger.debug(idlists)
    logger.debug(len(idlists))
    z.enricher('djfimlgenre', idlists)
    #z.redis.redis.lpos('cinema:filmids', '032b31a5-e63d-41ed-a851-8d757fa70c8e')
