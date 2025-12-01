import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

# Проверяем цветы, которые были обновлены недавно (с новыми timestamp)
# Ищем файлы с timestamp > 1764170000 (примерно после последнего обновления)
flowers = Flower.objects.all()[:15]

print("=" * 80)
print("ПРОВЕРКА ОБНОВЛЕННЫХ ЦВЕТОВ")
print("=" * 80)

for flower in flowers:
    if flower.image:
        # Проверяем timestamp в имени файла
        filename = flower.image.name
        print(f"\n{flower.name}:")
        print(f"  URL: http://localhost:8000{flower.image.url}")
