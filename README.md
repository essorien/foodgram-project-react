

## Описание
Проект "Продуктовый помошник" (Foodgram) предоставляет пользователям следующие возможности:

- регистрироваться
- создавать свои рецепты и управлять ими - (корректировать\удалять)
- просматривать рецепты других пользователей
- добавлять рецепты других пользователей в "Избранное" и в "Корзину"
- подписываться на других пользователей
- скачать список ингредиентов для рецептов, добавленных в "Корзину"

## Запуск локально

``` git@github.com:essorien/foodgram-project-react.git ```
### Создаём файл .env
```
SECRET_KEY=
DEBUG= 
ALLOWED_HOSTS= # разрешенные хосты
POSTGRES_DB= # имя базы данных
POSTGRES_USER= # логин для подключения к базе данных
POSTGRES_PASSWORD= # пароль для подключения к БД
DB_HOST= # название сервиса (контейнера)
DB_PORT= # порт для подключения к БД
```


### Cоздать и активировать виртуальное окружение:

```python -m venv venv
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```
### И установить зависимости из файла requirements.txt:

```python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### Из основной папки проекта выполнить команду:

``` 
docker-compose up -d
```
 - После успешного запуска контейнеров выполнить миграции:

 - ```docker-compose exec backend python manage.py migrate```
 - Создать суперюзера (Администратора):

- ``` docker-compose exec backend python manage.py createsuperuser ```
- Собрать статику:

- ```docker-compose exec backend python manage.py collectstatic --no-input ```

- Добавить ингредиенты в базу:
- ```docker-compose exec backend python manage.py load_json ```
## Теперь доступность проекта можно проверить по адресу http://localhost/

## Запуск на сервере
 Настраиваем внешний (серверный) Nginx, пример:

```server {
    server_name hachiroku.ddnsking.com;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/k92.tech/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/k92.tech/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = hachiroku.ddnsking.com) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name hachiroku.ddnsking.com;
    return 404;
} 
```
# Скопируйте из репозитория файлы, расположенные в директории infra:

- docker-compose.yml
- nginx.conf
# На сервере создайте директорию foodgram и поместите в неё файлы:

- docker-compose.production.yml
- nginx.conf
- .env

# В директории infra следует выполнить команды:

- ```docker-compose up -d```
- ```docker-compose exec backend python manage.py makemigrations```
- ```docker-compose exec backend python manage.py migrate```
- ```docker-compose exec backend python manage.py collectstatic```
# Для создания суперпользователя, выполните команду:
- ```docker-compose exec backend python manage.py createsuperuser```
Для добавления ингредиентов в базу данных, выполните команду:
- ```docker-compose exec backend python manage.py load_json```
- ```docker-compose exec backend python manage.py load_tag```
# После выполнения этих действий проект будет запущен и доступен по адресам:

- Главная страница: http://<адрес>/recipes/
- API проекта: http://<адрес>/api/
- Admin-зона: http://<адрес>/admin/


