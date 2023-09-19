

## Описание
Проект "Продуктовый помошник" (Foodgram) предоставляет пользователям следующие возможности:

- регистрироваться
- создавать свои рецепты и управлять ими - (корректировать\удалять)
- просматривать рецепты других пользователей
- добавлять рецепты других пользователей в "Избранное" и в "Корзину"
- подписываться на других пользователей
- скачать список ингредиентов для рецептов, добавленных в "Корзину"

## Клонируем проект

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
## Теперь доступность проекта можно проверить по адресу http://localhost/
