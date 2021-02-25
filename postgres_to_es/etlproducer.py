import os
from time import sleep

from dotenv import load_dotenv

from loguru import logger

if __name__ == '__main__':
    from etldecorator import backoff
    from etlredis import ETLRedis
    from etlpostgres import ETLPG
    from etlclasses import ETLProducerTable, ETLEnricherData
    from etldecorator import coroutine
else:
    from .etldecorator import backoff
    from .etlredis import ETLRedis
    from .etlpostgres import ETLPG
    from .etlclasses import ETLProducerTable, ETLEnricherData
    from .etldecorator import coroutine


class ETLProducer:
    producer_table = [
        ETLProducerTable(table='djfilmwork', isrelation=False),
        ETLProducerTable(table='djfilmperson', field='film_work_id', ptable='djfilmworkperson', pfield='person_id'),
        ETLProducerTable(table='djfilmgenre', field='film_work_id', ptable='djfilmworkgenre', pfield='genre_id'),
        ETLProducerTable(table='djfilmtype', field='id', ptable='djfilmwork', pfield='type_id'),
    ]

    def __init__(self, envfile='../.env'):
        dotenv_path = os.path.join(os.path.dirname(__file__), envfile)
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        self.limit = int(os.getenv('ETL_SIZE_LIMIT', '7'))

        self.redis = ETLRedis()
        self.pgbase = ETLPG()

    def worker(self, producer):
        """
        This function is initial Generator
        """
        while self.redis.get_status('producer') == 'run':
            for table in self.producer_table:
                #logger.debug(table)
                producer.send(table)
                sleep(1)
    
    @coroutine
    def producer(self, enricher):
        while True:
            data: ETLProducerTable = (yield)

            lasttime = self.redis.get_lasttime(data.table) or self.pgbase.get_first_object_time(data.table)
            idlist = self.pgbase.get_updated_object_id(lasttime, data.table, self.limit)
            try:
                #Why two last time ?
                lasttime = idlist[-1].modified
                lasttime = self.redis.set_lasttime(data.table, idlist[-1].modified)
            except IndexError:
                logger.debug(f'No more new data in {data.table}')
            idlist = [filmid.id for filmid in idlist]
            logger.debug(idlist)
            enricher.send(ETLEnricherData(data, idlist))
    
    @coroutine
    def enricher(self):
        while True:
            data: ETLEnricherData = (yield)
            offset = 0
            isupdatedid = True if len(data.idlist) > 0 else False
            while isupdatedid:
                filmids = (
                    self.pgbase.get_updated_film_id(data.table, tuple(data.idlist), self.limit, offset) 
                    if data.table.isrelation else data.idlist
                )
                [self.redis.push_filmid(id) for id in filmids]
                if (len(filmids) == self.limit) and (data.table.isrelation):
                    offset += self.limit
                else:
                    isupdatedid = False

    def start(self):
        #remove it
        self.redis.set_status('producer', 'stop')

        if self.redis.get_status('producer') == 'run':
            logger.debug('ETL Producer already started, please stop it before run!')
            return 
        else:
            self.redis.set_status('producer', 'run')
        
        enricher = self.enricher()
        producer = self.producer(enricher)
        self.worker(producer)

if __name__ == '__main__':
    ETLProducer().start()
