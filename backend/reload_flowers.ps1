# Script to update/add flowers to database
# IMPORTANT: Run this script from the backend directory!
Write-Host "Updating database with flowers..." -ForegroundColor Yellow
python manage.py shell -c "from flowers.parsers import FlowerParser; parser = FlowerParser(); flowers = parser.parse_flowers(); parser.save_flowers(flowers); print('Done! Total flowers:', len(flowers))"
Write-Host "Done!" -ForegroundColor Green
