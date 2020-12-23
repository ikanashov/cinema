import csv
import io
import uuid
from datetime import datetime, timezone

from etlclasses import MoviesGenre, MoviesPerson, MoviesToPostgres
from etlclasses import film_genre, film_person, film_work, film_work_genre, film_work_person


class CsvMovies:
    filmgenres: dict = {}
    filmpersons: dict = {}
    filmworks: dict = {}
    filmworkgenres: dict = {}
    filmworkpersons: dict = {}

    def get_or_add_film_genre(self, genre: MoviesGenre) -> film_genre:
        try:
            filmgenre = self.filmgenres[genre.name]
        except KeyError:
            now = datetime.now(timezone.utc)
            filmgenre = (str(uuid.uuid4()), genre.name, genre.name, f'from id = {genre.migrated_from}', now, now)
            self.filmgenres[genre.name] = filmgenre
        finally:
            return film_genre(*filmgenre)

    def get_or_add_film_person(self, person: MoviesPerson) -> film_person:
        try:
            filmperson = self.filmpersons[person.name]
        except KeyError:
            now = datetime.now(timezone.utc)
            filmperson = (
                str(uuid.uuid4()),
                person.name,
                None,
                f'imported from old_id = {person.migrated_from}',
                now,
                now
            )
            self.filmpersons[person.name] = filmperson
        finally:
            return film_person(*filmperson)

    def add_film_work(self, movie: MoviesToPostgres) -> film_work:
        now = datetime.now(timezone.utc)
        filmuuid = str(uuid.uuid4())
        filmwork = (filmuuid, movie.title, movie.plot, None, '', '', movie.imdb_rating, '', movie.id, now, now)
        self.filmworks[filmuuid] = filmwork
        return film_work(*filmwork)

    def add_genre_film_work(self, genre: film_work_genre) -> film_work_genre:
        gfwuuid = str(uuid.uuid4())
        genrefilmwork = (
            gfwuuid,
            genre.film_work_id, genre.genre_id,
            genre.migrated_from, datetime.now(timezone.utc)
        )
        self.filmworkgenres[gfwuuid] = genrefilmwork
        return film_work_genre(*genrefilmwork)

    def add_person_film_work(
            self, role: str, film_work_id: str, person_id: str, migrated_from: str) -> film_work_person:
        pfwuuid = str(uuid.uuid4())
        personfilmwork = (
            pfwuuid,
            film_work_id, person_id, role,
            migrated_from, datetime.now(timezone.utc)
        )
        self.filmworkpersons[pfwuuid] = personfilmwork
        return film_work_person(*personfilmwork)

    def add_or_get_film_work(self, movie: MoviesToPostgres) -> film_work:
        new_film_work = self.add_film_work(movie)
        for genre in movie.genres:
            filmgenre = self.get_or_add_film_genre(genre)
            self.add_genre_film_work(film_work_genre(None, new_film_work.id, filmgenre.id, movie.id, None))
        for person in movie.persons:
            filmperson = self.get_or_add_film_person(person)
            self.add_person_film_work(person.role, new_film_work.id, filmperson.id, movie.id)
        return new_film_work

    def generate_csv(self, tabledict: dict) -> io.StringIO:
        csvtable = io.StringIO()
        tablewriter = csv.writer(csvtable, delimiter='|',)
        for key in tabledict:
            tablewriter.writerow(tabledict[key])
        csvtable.seek(0)
        return csvtable
