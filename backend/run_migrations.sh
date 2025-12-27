#!/bin/bash
set -e  # Остановить при ошибке
echo "=========================================="
echo "Starting migrations..."
echo "=========================================="
python manage.py migrate --verbosity 2
echo "=========================================="
echo "Migrations completed successfully!"
echo "=========================================="
exec gunicorn wsgi:application --bind 0.0.0.0:${PORT:-10000}

