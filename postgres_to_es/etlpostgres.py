from logging import log
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from uuid import UUID

from loguru import logger

import psycopg2
from psycopg2 import sql


class ETLPG:
    UPDATED = 'SELECT id, modified FROM {} WHERE modified  > %s ORDER BY modified LIMIT %s'
    FILMGENREUPDATED = 'SELECT film_work_id, genre_id FROM djfilmworkgenre WHERE genre_id IN %s'
    FILMTYPEUPDATED = 'SELECT id, type_id FROM djfilmwork WHERE type_id IN %s'
    FILMPERSONUPDATED = 'SELECT film_work_id, person_id FROM djfilmworkperson WHERE person_id = ANY (%s::uuid[])'
    GETFILMBYID = '''
    SELECT 
        fw.id, fw.rating, fw.imdb_tconst, ft.name,
        ARRAY_AGG(DISTINCT fg.name ) AS genres,
        fw.title, fw.description,
        ARRAY_AGG(DISTINCT fp.id || ' : ' || fp.full_name) FILTER (WHERE fwp.role = 'director') AS directors,
        ARRAY_AGG(DISTINCT fp.id || ' : ' || fp.full_name) FILTER (WHERE fwp.role = 'actor') AS actors,
        ARRAY_AGG(DISTINCT fp.id || ' : ' || fp.full_name) FILTER (WHERE fwp.role = 'writer') AS writers,
        fw.modified
    FROM djfilmwork AS fw
    LEFT OUTER JOIN djfilmworkperson AS fwp ON fw.id = fwp.film_work_id 
    LEFT OUTER JOIN djfilmperson AS fp ON fwp.person_id = fp.id 
    LEFT OUTER JOIN djfilmworkgenre AS fwg ON fw.id = fwg.film_work_id 
    LEFT OUTER JOIN djfilmgenre AS fg ON fwg.genre_id = fg.id 
    INNER JOIN djfilmtype AS ft ON fw.type_id = ft.id 
    WHERE fw.id IN %s
    GROUP BY fw.id, ft.id
    '''
        
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

    def pg_single_query(self, sqlquery: str, queryargs: tuple) -> tuple:
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(sqlquery, queryargs)
            row = cur.fetchone()
        return row

    def pg_multy_query(self, sqlquery: str, queryargs: tuple) -> list:
        with self.conn as conn, conn.cursor() as cur:
            logger.debug(cur.mogrify(sqlquery, queryargs))
            cur.execute(sqlquery, queryargs)
            rows = cur.fetchall()
        return rows

    def get_updated_object_id(self, lasttime: datetime, table: str, limit: int) -> list:
        query = sql.SQL(self.UPDATED).format(sql.Identifier(table))
        rows = self.pg_multy_query(query, (lasttime, limit, ))
        logger.debug(rows)

    def get_filmgenreupdated_id(self, idlists: tuple) -> list:
        rows = self.pg_multy_query(self.FILMGENREUPDATED, (idlists,))
        logger.debug(rows)

    def get_filmtypeupdated_id(self, idlists: tuple) -> list:
        rows = self.pg_multy_query(self.FILMTYPEUPDATED, (idlists,))
        logger.debug(rows)

    def get_filmpersonupdated_id(self, idlists: tuple) -> list:
        rows = self.pg_multy_query(self.FILMPERSONUPDATED, (idlists,))
        logger.debug(rows)

    def get_filmsbyid(self, idlists: list) -> id:
        with self.conn.cursor() as cur:
            cur.execute(self.GETFILMBYID, (tuple(idlists), ))
            while row := cur.fetchone():
                logger.debug(row)


if __name__ == '__main__':
    lasttime = datetime.fromisoformat('2021-01-24 17:00:56.990682+00:00')
    logger.debug(lasttime)
    z = ETLPG()
    #z.get_updated_object_id(lasttime, 'djfilmperson', 10)
    #z.get_updated_object_id(lasttime, 'djfilmgenre', 10)
    #z.get_updated_object_id(lasttime, 'djfilmtype', 10)
    #z.get_filmgenreupdated_id(('a9b628f3-8438-4fdb-98e4-177102e36320', '71a4a4e5-948a-4a37-8052-efff2978ff74'))
    #z.get_filmgenreupdated_id(('a9b628f3-8438-4fdb-98e4-177102e36320', ))
    #z.get_filmtypeupdated_id(('e8751483-0a94-46e8-b136-9d5bbe2ffb7c', '5bd77168-c5b1-4c9d-bd1f-1193582d9e66'))
    z.get_filmpersonupdated_id(['d8b0b11b-8a24-4565-97e5-26844db628cb', 'b5da2459-aae3-4199-8b8d-e2fa25714bfa', '333'])
    #z.get_filmsbyid(['a6a4e4e5-886d-4d66-a2dc-d3165f6cb6a3', 'cabfe0b2-5151-460c-8362-2f889353f7ad', 'da2712f0-d4b7-4144-a868-259e3d34e018', 'da2712f0-d4b7-4144-a868-259e3d34e018'])