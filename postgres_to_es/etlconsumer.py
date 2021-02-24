from logging import log
import os
from datetime import date, datetime, timezone
from time import sleep

from dotenv import load_dotenv

from typing import List

from loguru import logger

if __name__ == '__main__':
    from etlelastic import ETLElastic
    from etlredis import ETLRedis
    from etlpostgres import ETLPG
    from etlclasses import ETLFilmWork, ESMovie, ESPerson
    from etldecorator import coroutine
else:
    from .etlelastic import ETLElastic
    from .etlredis import ETLRedis
    from .etlpostgres import ETLPG
    from .etlclasses import ETLFilmWork, ESMovie, ESPerson
    from .etldecorator import coroutine

class ETLConsumer:

    def __init__(self, envfile='../.env'):
        dotenv_path = os.path.join(os.path.dirname(__file__), envfile)
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        self.limit = int(os.getenv('ETL_SIZE_LIMIT', '7'))

        self.redis = ETLRedis()
        self.pgbase = ETLPG()
        self.es = ETLElastic()
    
    def get_filmsid_from_redis(self, putter) -> List[ETLFilmWork]:
        while self.redis.get_status('consumer') == 'run':
            logger.debug(self.limit)
            idlists = self.redis.get_filmid_for_work(self.limit)
            logger.debug(idlists)
            films = self.pgbase.get_filmsbyid(tuple(idlists)) if len(idlists) > 0 else []
            sleep(1)
            putter.send(films)
    
    @coroutine
    def put_films_to_ES(self) -> bool:
        while True:
            films: List[ETLFilmWork] = (yield)
            esfilms = [
                ESMovie(
                    film.id, film.rating, film.imdb_tconst, film.type_name, film.genres,
                    film.title, film.description,
                    [name.split(' : ')[1] for name in film.directors] if film.directors else None,
                    [name.split(' : ')[1] for name in film.actors] if film.actors else None,
                    [name.split(' : ')[1] for name in film.writers] if film.writers else None,
                    [ESPerson(*name.split(' : ')) for name in film.directors] if film.directors else None,
                    [ESPerson(*name.split(' : ')) for name in film.actors] if film.actors else None,
                    [ESPerson(*name.split(' : ')) for name in film.writers] if film.writers else None
                ) for film in films]
            if self.es.bulk_update(esfilms):
                self.redis.del_work_queuename()
                logger.debug('All ok delete working queue')

    def start(self):
        if self.redis.get_status('consumer') == 'run':
            logger.debug('ETL Consumer already started, please stop it before run!')
            return 
        else:
            self.redis.set_status('consumer', 'run')
        
        putter = self.put_films_to_ES()
        self.get_filmsid_from_redis(putter)

    def stop(self):
        self.redis.set_status('consumer', 'stop')
        logger.debug('consumer stopped')

if __name__ == '__main__':
    ETLConsumer().stop()
    ETLConsumer().start()
