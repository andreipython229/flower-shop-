Set-Location frontend
if (-not (Test-Path "node_modules")) {
    Write-Host "Установка зависимостей..." -ForegroundColor Green
    npm install
}
Write-Host "Запуск React сервера на http://localhost:3000" -ForegroundColor Green
npm start




