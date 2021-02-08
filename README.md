# E-cinema

Для запуска проекта необходимо создать в корне файл .env следующего содержимого

```shell
POSTGRES_DB=cinema
POSTGRES_USER=yandex
POSTGRES_PASSWORD=<>
POSTGRES_HOST=localhost
POSTGRES_PORT=7654
POSTGRES_SCHEMA=content,public,imdb
DJANGO_HOST=dev.usurt.ru
DJANGO_PORT=8354
NGINX_HTTP_PORT=8080
```

Пароль можно сгенерировать с помощью команды: ```openssl rand -hex 32```


 sudo docker-compose run etlcinema sh

/etl # cd db
/etl/db # ./get_imdb_data.sh

Поправить схему imdb 

Перенести create_schema в корень
Добавить в него psql
sudo docker-compose exec -T postgrescinema psql postgresql://yandex:DUBIDU@localhost:5432/cinema -A -t < db/schema_design/create_imdb_db_schema.sql

sudo docker-compose run etlcinema python /etl/load_imdb.py

sudo docker-compose exec djangocinema /cinema_admin/manage.py makemigrations
sudo docker-compose exec djangocinema /cinema_admin/manage.py migrate
sudo docker-compose exec djangocinema /cinema_admin/manage.py createsuperuser
sudo docker-compose exec djangocinema /cinema_admin/manage.py collectstatic

sudo docker-compose run etlcinema python /etl/dj_load_data.py

./stop

