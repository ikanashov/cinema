import io
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

import psycopg2


class DJNewMovies:
    SQLCREATEGENREINDEX = '''CREATE UNIQUE INDEX film_work_genre_ind
                                ON content.film_work_genre (film_work_id, genre_id)'''
    SQLCREATETYPEINDEX = '''CREATE UNIQUE INDEX film_work_type_ind
                                ON content.film_work_type (film_work_id, type_id)'''
    SQLCREATEPERSONINDEX = '''CREATE UNIQUE INDEX film_work_person_role_ind
                                ON content.film_work_person (film_work_id, person_id, role)'''
    SQLDROPGENREINDEX = '''DROP INDEX film_work_genre_ind'''
    SQLDROPTYPEINDEX = '''DROP INDEX film_work_type_ind'''    
    SQLDROPPERSONINDEX = '''DROP INDEX film_work_person_role_ind'''

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

    def drop_film_genre_index(self):
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLDROPGENREINDEX)

    def drop_film_type_index(self):
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLDROPTYPEINDEX)

    def drop_film_person_index(self):
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLDROPPERSONINDEX)

    def create_film_genre_index(self):
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLCREATEGENREINDEX)

    def create_film_type_index(self):
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLCREATETYPEINDEX)

    def create_film_person_index(self):
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLCREATEPERSONINDEX)

    def copy_to_csv_from_table(self, tablename: str) -> io.StringIO:
        csvtable = io.StringIO()
        with self.conn as conn, conn.cursor() as cur:
            cur.copy_to(csvtable, tablename, sep='|')
        csvtable.seek(0)
        return csvtable

    def copy_to_table_from_csv(self, tablename: str, csvtable: io.StringIO):
        with self.conn as conn, conn.cursor() as cur:
            cur.copy_from(csvtable, tablename, sep='|')
