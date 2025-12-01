Write-Host "Установка зависимостей..." -ForegroundColor Green
cd backend
pip install -r requirements.txt

Write-Host "`nВыполнение миграций..." -ForegroundColor Green
python manage.py migrate

Write-Host "`nЗапуск сервера Django..." -ForegroundColor Green
python manage.py runserver

