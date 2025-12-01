"""
Скрипт для поиска букетов на позициях 51-62
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

# Получаем все цветы в порядке, как они отображаются в каталоге
flowers = Flower.objects.filter(in_stock=True).order_by("id")

print("=" * 80)
print("БУКЕТЫ НА ПОЗИЦИЯХ 51-62:")
print("=" * 80)

# Позиции 51-62 (индексы 50-61, так как начинаем с 1)
target_flowers = list(flowers[50:62])  # Срез с 50 по 61 включительно

for idx, flower in enumerate(target_flowers, start=51):
    image_name = flower.image.name if flower.image else "Нет"
    print(
        f"{idx:3d}. {flower.name:60s} | ID: {flower.id} | "
        f"Изображение: {image_name[:40]}"
    )

print("")
print(f"Всего найдено: {len(target_flowers)} букетов")
