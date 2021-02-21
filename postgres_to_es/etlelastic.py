import os
import io
import json

from dotenv import load_dotenv

from elasticsearch import Elasticsearch, TransportError

from loguru import logger

from dataclasses import asdict

from esindex import CINEMA_INDEX_BODY as esbody
from etlclasses import ESPerson, ESMovie

class ETLElastic:
    def __init__(self, envfile='../.env'):
        dotenv_path = os.path.join(os.path.dirname(__file__), envfile)
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

        self.hosts = [os.getenv('ELASTIC_HOST', 'localhost')]
        self.port = os.getenv('ELASTIC_PORT', '9200')
        self.scheme = os.getenv('ELASITC_SCHEME', 'http')
        self.http_auth = (os.getenv('ELASTIC_USER', 'elastic'), os.getenv('ELASTIC_PASSWORD',''))
        self.index_name = os.getenv('ELASTIC_INDEX', 'test')
        self.es = Elasticsearch(self.hosts, port=self.port, scheme=self.scheme, http_auth=self.http_auth)


    def create_index(self, index_name='', index_body=''):
        try:
            result = self.es.indices.create(index_name, body=index_body)
            logger.debug(result)
        except TransportError as error:
            logger.debug('Error while creating an index')
            logger.debug(error)
            logger.debug(error.info)
    
    def bulk_update(self, docs: list) -> dict:
        body = ''
        for doc in docs:
            index = {'index' : {'_index' : self.index_name, '_id' : doc.id } }
            body += json.dumps(index) + '\n' + json.dumps(asdict(doc)) + '\n'
        results = self.es.bulk(body)
        logger.debug(results)
        return results


if __name__ == '__main__':
    z = ETLElastic()
    logger.debug(f'Elastic is alive ? {z.es.ping()}')
    z.create_index(index_name='test', index_body=esbody)

    test_persons = [ESPerson('ddfg-gdgg', 'Ivan Kanashov'), ESPerson('ddfg-gdfg', 'Nikita Kanashov'), ESPerson('gdfg-gdfg', 'Galina Kanashova')]
    tid = 'fdfdf-fdfg-dgdg'
    ttitle = 'Movie about all movies'
    tdirectors_names = [person.name for person in test_persons]
    tdirectors = test_persons
    test_elastic_1 = ESMovie(
        id=tid, title=ttitle, directors_names=tdirectors_names, directors=tdirectors,
        imdb_rating=0.0, imdb_tconst='', filmtype='', genre='', description='',
        writers_names='', actors_names='', actors =[], writers=[]
    )
        
    test_persons = [ESPerson('ddfadfg-gdgg', 'Ivan Kana'), ESPerson('dgdfg-gdhfg', 'Nik Kana'), ESPerson('ggdfg-gdfg', 'Gal Kanash')]
    tid = 'eeedf-fdfg-dgdg'
    ttitle = 'Second Movie'
    tdirectors_names = [person.name for person in test_persons]
    tdirectors = test_persons
    test_elastic_2 = ESMovie(
        id=tid, title=ttitle, directors_names=tdirectors_names, directors=tdirectors,
        imdb_rating=0.0, imdb_tconst='', filmtype='', genre='', description='',
        writers_names='', actors_names='', actors =[], writers=[]
    )

    list_test = [test_elastic_1, test_elastic_2]

    results = z.bulk_update(list_test)
    #for result in results['items']:
        #if result['index']['status'] != 200:
            #print(result['index'])

    res = z.es.search(index="test", body={"query": {"match_all": {}}})
    print("Got %d Hits:" % res['hits']['total']['value'])
