import os
import time


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


if __name__ == '__main__':
    start = time.time()
    IMDBMovies().load_data_from_tsv()
    end = time.time()
    print('Read tsv imdb files and write to postgres: ', (end-start), 'sec')
