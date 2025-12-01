@echo off
cd backend
echo Установка зависимостей...
pip install -r requirements.txt
echo.
echo Выполнение миграций...
python manage.py migrate
echo.
echo Запуск сервера Django...
python manage.py runserver
pause

