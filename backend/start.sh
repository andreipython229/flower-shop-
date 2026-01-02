#!/bin/bash
# Скрипт запуска для Render
# Выполняет миграции и запускает gunicorn

set -e  # Остановка при ошибке

echo "Выполнение миграций..."
python manage.py migrate --noinput

echo "Запуск gunicorn..."
exec gunicorn wsgi:application --bind 0.0.0.0:$PORT
