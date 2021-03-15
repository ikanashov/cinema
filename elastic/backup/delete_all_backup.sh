#!/bin/bash
echo 'Command for delete all backup for ' ${ELASTIC_INDEX} 'index'

AUTH="--user ${ELASTIC_USER}:${ELASTIC_PASSWORD}"

echo curl $AUTH -X DELETE "localhost:9200/_snapshot/${ELASTIC_INDEX}/snap*?pretty"
