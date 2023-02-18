# **Проект yamdb_final**
![yamdb workflow](https://github.com/jeniavoropay/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
## **Описание**
Проект собирает отзывы пользователей на произведения (Titles).
Произведения делятся на категории (Category): «Книги», «Фильмы», «Музыка». Сами произведения проект не хранит: нельзя посмотреть фильм или послушать музыку. Произведению может быть присвоен жанр (Genre) из списка предустановленных (например «Сказка», «Рок» или «Артхаус»). Новые произведения может добавлять только администратор, он же может расширять список категорий и жанров. 
Пользователи оставляют к произведениям текстовые отзывы (Review) и ставят оценку в диапазоне от одного до десяти (целое число); из оценок формируется усреднённая оценка — рейтинг. На одно произведение пользователь может оставить только один отзыв.
### Технологии
- Python 3.7
- Django 2.2.16
- Django Rest Framework 3.12.4
- PostgreSQL 13.0
### Авторы
- Евгения Воропай | [jeniavoropay](https://github.com/jeniavoropay)
- Владимир Васильев | [chem1sto](https://github.com/chem1sto)
- Павел Вервейн | [hive937](https://github.com/hive937)
## **Как запустить проект**
Клонировать репозиторий:
```
git clone https://github.com/jeniavoropay/yamdb_final.git
```
Создать _.env_ файл в директории _infra_ с переменными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<название-БД>
POSTGRES_USER=<имя-пользователя>
POSTGRES_PASSWORD=<пароль>
DB_HOST=db
DB_PORT=5432
```
Собрать образ из папки _infra_:
```
docker-compose up -d --build
```
Создать и применить миграции:
```
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```
Cобрать статику: 
```
docker-compose exec web python manage.py collectstatic --no-input
```
Создать суперпользователя для доступа к админке:
```
docker-compose exec web python manage.py createsuperuser
```
Из корневой директории выполнить команду для загрузки данных в БД:
```
docker-compose exec web python manage.py loaddata fixtures.json
```
## **Документация**
Доступна на [Redoc](http://localhost/redoc/).

