#!/bin/bash
echo 'Create backup for' ${ELASTIC_INDEX} 'index'

AUTH="--user ${ELASTIC_USER}:${ELASTIC_PASSWORD}"

curl $AUTH -X PUT "localhost:9200/_snapshot/${ELASTIC_INDEX}?pretty" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "'${ELASTIC_INDEX}'",
    "compress": true
  }
}
'

echo "Restore current snapshot"
curl $AUTH -X POST \
"localhost:9200/_snapshot/${ELASTIC_INDEX}/current/_restore?pretty" \
-H 'Content-Type: application/json' -d'
{
  "indices": "'${ELASTIC_INDEX}'",
  "ignore_unavailable": true,
  "include_global_state": true
}
'