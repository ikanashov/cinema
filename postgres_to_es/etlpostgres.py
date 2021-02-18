import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from loguru import logger

import psycopg2
from psycopg2 import sql


class ETLPG:
    UPDATED = 'SELECT id, modified FROM {} WHERE modified  > %s ORDER BY modified LIMIT %s'
    FILMGENREUPDATED = 'SELECT film_work_id, genre_id FROM djfilmworkgenre WHERE genre_id = %s'
    FILMTYPEUPDATED = 'SELECT id, type_id FROM djfilmwork WHERE type_id = %s'
    FILMPERSONUPDATED = 'SELECT film_work_id, person_id FROM djfilmworkperson WHERE person_id = %s'
        
    def __init__(self, envfile='../.env'):
        dotenv_path = os.path.join(os.path.dirname(__file__), envfile)
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

        self.conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            options='-c search_path=' + os.getenv('POSTGRES_SCHEMA', 'public'),
        )
  
    def get_updated_object_id(self, lasttime: datetime, table: str, limit: int) -> id:
        query = sql.SQL(self.UPDATED).format(sql.Identifier(table))
        logger.debug(query)
        with self.conn.cursor() as cur:
            cur.execute(query, (lasttime, limit, ))
            while row := cur.fetchone():
                logger.debug(row)

    def get_filmgenreupdated_id(self, idlists: list) -> id:
        for id in idlists:
            with self.conn.cursor() as cur:
                cur.execute(self.FILMGENREUPDATED, (id,))
                while row := cur.fetchone():
                    logger.debug(row)

    def get_filmtypeupdated_id(self, idlists: list) -> id:
        for id in idlists:
            with self.conn.cursor() as cur:
                cur.execute(self.FILMTYPEUPDATED, (id,))
                while row := cur.fetchone():
                    logger.debug(row)

    def get_filmpersonupdated_id(self, idlists:list) -> id:
        for id in idlists:
            with self.conn.cursor() as cur:
                cur.execute(self.FILMPERSONUPDATED, (id,))
                while row := cur.fetchone():
                    logger.debug(row)


if __name__ == '__main__':
    lasttime = datetime.fromisoformat('2021-01-24 17:00:56.990682+00:00')
    logger.debug(lasttime)
    z = ETLPG()
    #z.get_updated_object_id(lasttime, 'djfilmperson', 10)
    #z.get_updated_object_id(lasttime, 'djfilmgenre', 10)
    #z.get_updated_object_id(lasttime, 'djfilmtype', 10)
    #z.get_filmgenreupdated_id(['a9b628f3-8438-4fdb-98e4-177102e36320', '5bd77168-c5b1-4c9d-bd1f-1193582d9e66'])
    #z.get_filmtypeupdated_id(['e8751483-0a94-46e8-b136-9d5bbe2ffb7c'])
    z.get_filmpersonupdated_id(['d8b0b11b-8a24-4565-97e5-26844db628cb'])
    
