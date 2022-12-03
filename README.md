# RuTwit

Как поднять проект

### Команда для установки ВО
python3 -m venv venv

### Запуск ВО
source venv/bin/activate

### Установка зависимостей
pip install -r requirements.txt 

### Переход в каталог 
cd yatube

### Создание миграций 
python manage.py makemigrations

### Запуск миграций 
python manage.py migrate

### Запуск проекта 
python manage.py runserver

### Запустит все тесты проекта
python3 manage.py test