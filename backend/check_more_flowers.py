import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

# Проверяем первые 30 цветов
flowers = Flower.objects.all()[:30]

print("=" * 80)
print("ПРОВЕРКА ИЗОБРАЖЕНИЙ ЦВЕТОВ")
print("=" * 80)

for flower in flowers:
    print(f"\n{flower.name}:")
    if flower.image:
        print(f"  Изображение: {flower.image.name}")
        print(f"  URL: http://localhost:8000{flower.image.url}")
    else:
        print("  Нет изображения")
