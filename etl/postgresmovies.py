import io
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

import psycopg2

from etlclasses import Genre, MoviesToPostgres, Person
from etlclasses import film_genre, film_person, film_work, genre_film_work, person_film_work


class NewMovies:
    SQLGETONEGENRE = '''SELECT * FROM genre WHERE name = %s'''
    SQLINSERTGENRE = '''INSERT INTO genre (
                                    id, name, description,
                                    migrated_from,
                                    created_at, updated_at)
                               VALUES (%s, %s, %s, %s, %s, %s)
                               RETURNING *'''
    SQLGETONEPERSON = '''SELECT * FROM person WHERE full_name = %s'''
    SQLINSERTPERSON = '''INSERT INTO person (
                                    id, full_name, birth_date,
                                    migrated_from,
                                    created_at, updated_at)
                               VALUES (%s, %s, %s, %s, %s, %s)
                               RETURNING *'''
    SQLGETONEMOVIE = '''SELECT * FROM film_work WHERE migrated_from = %s'''
    SQLINSERTMOVIE = '''INSERT INTO film_work (
                                    id, title, description,
                                    rating,
                                    migrated_from,
                                    created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                RETURNING *'''
    SQLINSERTGENREFW = '''INSERT INTO genre_film_work (
                                      id, film_work_id, genre_id,
                                      migrated_from, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                                RETURNING *'''
    SQLINSERTPERSONFW = '''INSERT INTO person_film_work (
                                      id, film_work_id, person_id, role,
                                      migrated_from, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                RETURNING *'''
    SQLCREATEGENREINDEX = '''CREATE UNIQUE INDEX film_work_genre
                                ON content.genre_film_work (film_work_id, genre_id)'''
    SQLCREATEPERSONINDEX = '''CREATE UNIQUE INDEX film_work_person_role
                                ON content.person_film_work (film_work_id, person_id, role)'''
    SQLDROPGENREINDEX = '''DROP INDEX film_work_genre'''
    SQLDROPPERSONINDEX = '''DROP INDEX film_work_person_role'''

    def __init__(self):
        dotenv_path = os.path.join(os.path.dirname(__file__), '../postgresql/.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            POSTGRES_DB = os.getenv('POSTGRES_DB')
            POSTGRES_USER = os.getenv('POSTGRES_USER')
            POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

        self.conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host='localhost',
            port=5432,
            options='-c search_path=content',
        )

    def check_film_genre(self, genre: Genre) -> film_genre:
        with self.conn.cursor() as cur:
            cur.execute(self.SQLGETONEGENRE, (genre.name,))
            row = cur.fetchone()
        if row:
            return film_genre(*row)

    def add_film_genre(self, genre: Genre) -> film_genre:
        now = datetime.now(timezone.utc)
        newgenre = (str(uuid.uuid4()), genre.name, genre.name, f'from movie_id = {genre.migrated_from}', now, now)
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLINSERTGENRE, newgenre)
            row = cur.fetchone()
        if row:
            return film_genre(*row)

    def get_or_add_film_genre(self, genre: Genre) -> film_genre:
        film_genre = self.check_film_genre(genre)
        if film_genre:
            return film_genre
        else:
            film_genre = self.add_film_genre(genre)
            return film_genre

    def check_film_person(self, person: Person) -> film_person:
        with self.conn.cursor() as cur:
            cur.execute(self.SQLGETONEPERSON, (person.name,))
            row = cur.fetchone()
        if row:
            return film_person(*row)

    def add_film_person(self, person: Person) -> film_person:
        now = datetime.now(timezone.utc)
        newperson = (str(uuid.uuid4()), person.name, None, f'imported old_id = {person.migrated_from}', now, now)
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLINSERTPERSON, newperson)
            row = cur.fetchone()
        if row:
            return film_person(*row)

    def get_or_add_film_person(self, person: Person) -> film_person:
        film_person = self.check_film_person(person)
        if film_person:
            return film_person
        else:
            film_person = self.add_film_person(person)
            return film_person

    def check_film_work(self, movie: MoviesToPostgres) -> film_work:
        with self.conn.cursor() as cur:
            cur.execute(self.SQLGETONEMOVIE, (movie.id,))
            row = cur.fetchone()
        if row:
            return film_work(*row)

    def add_film_work(self, movie: MoviesToPostgres) -> film_work:
        now = datetime.now(timezone.utc)
        new_film_work = (str(uuid.uuid4()), movie.title, movie.plot, movie.imdb_rating, movie.id, now, now)
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLINSERTMOVIE, new_film_work)
            row = cur.fetchone()
        if row:
            return film_work(*row)

    def add_genre_film_work(self, genre: genre_film_work) -> genre_film_work:
        film_genre = (str(uuid.uuid4()),
                      genre.film_work_id, genre.genre_id,
                      genre.migrated_from, datetime.now(timezone.utc))
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLINSERTGENREFW, film_genre)
            row = cur.fetchone()
        if row:
            return genre_film_work(*row)

    def add_person_film_work(
            self, role: str, film_work_id: str, person_id: str, migrated_from: str) -> person_film_work:
        film_person = (str(uuid.uuid4()),
                       film_work_id, person_id, role,
                       migrated_from, datetime.now(timezone.utc))
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLINSERTPERSONFW, film_person)
            row = cur.fetchone()
        if row:
            return person_film_work(*row)

    def add_or_get_film_work(self, movie: MoviesToPostgres) -> film_work:
        film_work = self.check_film_work(movie)
        if film_work:
            return film_work
        else:
            new_film_work = self.add_film_work(movie)
            for genre in movie.genres:
                film_genre = self.get_or_add_film_genre(genre)
                self.add_genre_film_work(genre_film_work(None, new_film_work.id, film_genre.id, movie.id, None))
            for person in movie.persons:
                film_person = self.get_or_add_film_person(person)
                self.add_person_film_work(person.role, new_film_work.id, film_person.id, movie.id)
            return new_film_work

    def drop_film_genre_index(self):
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLDROPGENREINDEX)

    def drop_film_person_index(self):
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLDROPPERSONINDEX)

    def create_film_genre_index(self):
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(self.SQLCREATEGENREINDEX)

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
            cur.copy_from(csvtable, tablename, sep='|', null='')
