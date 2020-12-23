import os
import time
import http.client


from dotenv import load_dotenv

import psycopg2


class IMDBMovies:
    TSVTABLES = {
        'name_basics': '../db/name.basics.tsv',
        'title_basics': '../db/title.basics.tsv',
        'title_episode': '../db/title.episode.tsv',
    }

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

    def copy_to_table_from_csv(self, tablename: str, csvobject):
        """Copy data to tablename table.
        TRUNCATE table before copy data!
        """
        with self.conn as conn, conn.cursor() as cur:
            cur.execute('TRUNCATE ' + tablename)
            cur.copy_from(csvobject, tablename, sep='\t')

    def load_data_from_tsv(self):
        for table, filename in self.TSVTABLES.items():
            with open(filename) as tsvfile:
                # Read line with header
                tsvfile.readline()
                self.copy_to_table_from_csv(table, tsvfile)
    
    def get_imdb_id_by_https(self, imdb_tconst: str) -> str:
        conn = http.client.HTTPSConnection('www.imdb.com')
        conn.request('GET', f'/title/{imdb_tconst}/')
        response = conn.getresponse()
        if response.code == 301:
            dictheaders = [(value) for key,value in response.getheaders() if key == 'Location']
            url = dictheaders[0]
            imdb_tconst = url.split('/')[2]
            return imdb_tconst
        else:
            return None
        


if __name__ == '__main__':
    empty_id = ['tt0281088', 'tt1037715', 'tt2208084', 'tt0429437', 'tt3124492', 'tt0414758', 'tt1498189', 'tt0112271']
    start = time.time()
    #IMDBMovies().load_data_from_tsv()
    for movie_id in empty_id:
        print(IMDBMovies().get_imdb_id_by_https(movie_id))
    end = time.time()
    print('Read tsv imdb files and write to postgres: ', (end-start), 'sec')
