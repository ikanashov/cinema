from csvmovies import CsvMovies

from postgresmovies import NewMovies

from sqlitemovies import SQLiteMoviesDB


def load_from_sqlite():
    sqlite_movies = SQLiteMoviesDB().get_all_movies()
    csv_movies = CsvMovies()
    postgres_movies = NewMovies()

    [csv_movies.add_or_get_film_work(movie) for movie in sqlite_movies]

    genres = csv_movies.generate_csv(csv_movies.genres)
    persons = csv_movies.generate_csv(csv_movies.persons)
    filmworks = csv_movies.generate_csv(csv_movies.filmworks)
    genresfilmworks = csv_movies.generate_csv(csv_movies.genresfilmworks)
    personsfilmworks = csv_movies.generate_csv(csv_movies.personsfilmworks)

    postgres_movies.drop_film_genre_index()
    postgres_movies.drop_film_person_index()

    postgres_movies.copy_to_table_from_csv('genre', genres)
    postgres_movies.copy_to_table_from_csv('person', persons)
    postgres_movies.copy_to_table_from_csv('film_work', filmworks)
    postgres_movies.copy_to_table_from_csv('genre_film_work', genresfilmworks)
    postgres_movies.copy_to_table_from_csv('person_film_work', personsfilmworks)

    postgres_movies.create_film_genre_index()
    postgres_movies.create_film_person_index()


if __name__ == '__main__':
    load_from_sqlite()
