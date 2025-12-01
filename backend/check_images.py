import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

print("Проверка изображений в базе данных:")
print("=" * 60)

flowers = Flower.objects.all()[:20]
has_image = 0
no_image = 0

for flower in flowers:
    if flower.image:
        print(f"✓ {flower.name}: {flower.image.name}")
        has_image += 1
    else:
        print(f"✗ {flower.name}: НЕТ ИЗОБРАЖЕНИЯ")
        no_image += 1

print("=" * 60)
print(f"С изображениями: {has_image}")
print(f"Без изображений: {no_image}")
print(f"Всего проверено: {len(flowers)}")
