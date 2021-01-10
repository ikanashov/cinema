import time

from csvmovies import CsvMovies
from imdbmovies import IMDBMovies
from sqlitemovies import SQLiteMoviesDB


if __name__ == '__main__':
    empty_id = ['tt0281088', 'tt1037715', 'tt2208084', 'tt0429437', 'tt3124492', 'tt0414758', 'tt1498189', 'tt0112271',
                'tt10323338', 'tt7589570', 'tt0092455', 'tt2208084', 'tt22084'
                ]
    z = CsvMovies()
    start = time.time()
    #IMDBMovies().load_data_from_tsv()
    #for movie_id in empty_id:
        #print(IMDBMovies().get_imdb_id_by_https(movie_id))
    sqlite_movies = SQLiteMoviesDB().get_all_movies()
    for movie in sqlite_movies:
    #for movie_id in empty_id:
        #print()
        for person in movie.persons:
            imn = IMDBMovies().get_imdb_person_by_name(person.name, person.role, movie.id)
            
            if (imn):
                pass
            else:
                print(person.name, person.role, movie.id)
            #print('##start##')
            #print(movie.id, person.name)
            #print()
            #print(IMDBMovies().get_imdb_person_by_name(person.name, movie.id))
            #print('##end##')
        #print(z.add_film_work(movie, IMDBMovies().get_imdb_movie_by_id(movie.id)))
        #mov = IMDBMovies().get_imdb_movie_by_id(movie.id)
        #print(IMDBMovies().get_imdb_movie_by_id(movie.id))
    end = time.time()
    print('Read tsv imdb files and write to postgres: ', (end-start), 'sec')
