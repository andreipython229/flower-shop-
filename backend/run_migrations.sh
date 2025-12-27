#!/bin/bash
echo "=========================================="
echo "Starting migrations..."
echo "=========================================="
python manage.py migrate --verbosity 2
MIGRATE_EXIT_CODE=$?
echo "=========================================="
echo "Migrations exit code: $MIGRATE_EXIT_CODE"
echo "=========================================="
if [ $MIGRATE_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Migrations failed!"
    exit $MIGRATE_EXIT_CODE
fi
echo "Migrations completed successfully!"
echo "=========================================="

