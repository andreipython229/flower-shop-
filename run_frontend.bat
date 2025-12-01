@echo off
cd frontend
if not exist "node_modules" (
    echo Установка зависимостей...
    call npm install
)
echo Запуск React сервера на http://localhost:3000
call npm start




