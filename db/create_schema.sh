#!/bin/bash

# Забираем переменные настройки postgreSQL для поключения 
source ../.env
POSTGRES_URI="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

#Запускаем скрипт генерирующий схему базы данных
#psql $POSTGRES_URI -A -q -t -f create_cinema_db_schema.sql
echo sudo docker-compose exec postgrescinema $POSTGRES_URI -A -q -t -f schema_design/create_content_db_schema.sql
echo sudo docker-compose exec postgrescinema $POSTGRES_URI -A -q -t -f schema_design/create_imdb_db_schema.sql
