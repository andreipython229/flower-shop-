"""
Проверка текущих изображений в базе данных
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.conf import settings

from flowers.models import Flower

print("=" * 80)
print("ПРОВЕРКА ТЕКУЩИХ ИЗОБРАЖЕНИЙ")
print("=" * 80)

flowers = Flower.objects.all()[:4]  # Первые 4 для проверки

for flower in flowers:
    print(f"\n{flower.name}:")
    if flower.image:
        print(f"  Файл: {flower.image.name}")
        file_path = os.path.join(settings.MEDIA_ROOT, flower.image.name)
        if os.path.exists(file_path):
            import time

            mtime = os.path.getmtime(file_path)
            print(f"  Путь: {file_path}")
            print(f"  Время модификации: {time.ctime(mtime)}")
            print(f"  Размер: {os.path.getsize(file_path)} байт")
        else:
            print("  ✗ Файл не существует!")
    else:
        print("  ✗ Нет изображения")
