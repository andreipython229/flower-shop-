@echo off
REM Активация виртуального окружения если есть
if exist "..\.venv\Scripts\activate.bat" (
    call "..\.venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

cd backend
if not exist "db.sqlite3" (
    echo Выполнение миграций...
    python manage.py migrate
)
echo Запуск Django сервера на http://localhost:8000
python manage.py runserver

