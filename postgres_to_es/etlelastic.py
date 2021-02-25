import os
import json

from dotenv import load_dotenv

from elasticsearch import Elasticsearch, TransportError, ConnectionError

from time import sleep

from loguru import logger

from dataclasses import asdict

from esindex import CINEMA_INDEX_BODY as esbody
from etlclasses import ESPerson, ESMovie
from etldecorator import backoff

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
        
        self.es = self.connect()
        #self.create_index()

        self.create_index(self.index_name, esbody)

    def connect(self) -> Elasticsearch:
        return Elasticsearch(self.hosts, port=self.port, scheme=self.scheme, http_auth=self.http_auth)
        
    
    #@backoff(0.00001)
    def is_connected(self) -> bool:
        try:
            self.es.cluster.health(wait_for_status='yellow')
            logger.debug('I am in is_connected')
            return True
        except ConnectionError:
            logger.debug('I am in connection error is_connected')
            raise
            
    
    @backoff(1)
    def create_index(self, index_name='', index_body=''):
        #self.es = self.es if self.is_connected() else self.connect()
        try:
            result = self.es.indices.create(index_name, body=index_body)
            logger.debug(result)
        except TransportError as error:
            #logger.debug('Error while creating an index')
            logger.debug(error)
            #logger.debug(error.info)
           
    @backoff(1)
    def bulk_update(self, docs: list) -> dict:
        if docs == []:
            logger.debug('No more data to update in elastic')
            return None
        body = ''
        for doc in docs:
            index = {'index' : {'_index' : self.index_name, '_id' : doc.id } }
            body += json.dumps(index) + '\n' + json.dumps(asdict(doc)) + '\n'

        results = self.es.bulk(body)
        if results['errors']:
            error = [result['index'] for result in results['items'] if result['index']['status'] != 200]
            logger.debug(results['took'])
            logger.debug(results['errors'])
            logger.debug(error)
            return None
        return True
