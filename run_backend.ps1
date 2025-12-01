# Активация виртуального окружения если есть
if (Test-Path "..\.venv\Scripts\Activate.ps1") {
    & "..\.venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

Set-Location backend
if (-not (Test-Path "db.sqlite3")) {
    Write-Host "Выполнение миграций..." -ForegroundColor Green
    python manage.py migrate
}
Write-Host "Запуск Django сервера на http://localhost:8000" -ForegroundColor Green
python manage.py runserver

