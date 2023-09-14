Проект foodgram:
    Автор: Потапенко Семён Михайлович

Суть проекта:
    Возможность выкладывать свои рецепты, подписываться на авторов других рецептов,
    добавлять рецепты в избранное и список покупок, проект поддерживает регистрацию и авторизацию пользователей.

Инструкция к запуску.

Как запустить проект: Клонировать репозиторий и перейти в него в командной строке:

git clone git@github.com:semenpotapenko26/foodgram-project-react.git

Cоздать и активировать виртуальное окружение:

python3 -m venv env source env/bin/activate Установить зависимости из файла requirements.txt:

python3 -m pip install --upgrade pip pip install -r requirements.txt

Выполнить миграции:

python3 manage.py migrate Запустить проект:

python3 manage.py runserver

Некоторые примеры использования запросов:

Получить список всех пользователей:

GET api/users/

Добавить новый рецепт:

POST api/кусшзуы/

Получить список ингредиентов:

GET api/ingredients/