import time

from djcsvmovies import DJCsvMovies

from djpostgresmovies import DJNewMovies

from sqlitemovies import SQLiteMoviesDB


def load_from_sqlite():
    sqlite_movies = SQLiteMoviesDB().get_all_movies()
    csv_movies = DJCsvMovies()
    postgres_movies = DJNewMovies()

    [csv_movies.add_or_get_film_work(movie) for movie in sqlite_movies]

    filmgenres = csv_movies.generate_csv(csv_movies.filmgenres)
    filmpersons = csv_movies.generate_csv(csv_movies.filmpersons)
    filmtypes = csv_movies.generate_csv(csv_movies.filmtypes)
    filmworks = csv_movies.generate_csv(csv_movies.filmworks)
    filmworkgenres = csv_movies.generate_csv(csv_movies.filmworkgenres)
    filmworkpersons = csv_movies.generate_csv(csv_movies.filmworkpersons)

    #postgres_movies.drop_film_genre_index()
    #postgres_movies.drop_film_type_index()
    #postgres_movies.drop_film_person_index()

    postgres_movies.copy_to_table_from_csv('djfilmgenre', filmgenres)
    postgres_movies.copy_to_table_from_csv('djfilmperson', filmpersons)
    postgres_movies.copy_to_table_from_csv('djfilmtype', filmtypes)
    postgres_movies.copy_to_table_from_csv('djfilmwork', filmworks)
    postgres_movies.copy_to_table_from_csv('djfilmworkgenre', filmworkgenres)
    postgres_movies.copy_to_table_from_csv('djfilmworkperson', filmworkpersons)

    #postgres_movies.create_film_genre_index()
    #postgres_movies.create_film_type_index()
    #postgres_movies.create_film_person_index()


if __name__ == '__main__':
    start = time.time()
    load_from_sqlite()
    end = time.time()
    print('Read tsv imdb files and write to postgres: ', (end-start), 'sec')
