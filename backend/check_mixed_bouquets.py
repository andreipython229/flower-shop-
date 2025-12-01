"""
Скрипт для проверки смешанных букетов
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

# Ищем все смешанные букеты и другие проблемные
bouquets = (
    Flower.objects.filter(name__icontains="смешанный").order_by("id")
    | Flower.objects.filter(name__icontains="букет невесты").order_by("id")
    | Flower.objects.filter(name__icontains="свадебный").order_by("id")
)

all_bouquets = Flower.objects.filter(in_stock=True).order_by("id")

print("=" * 80)
print("ВСЕ БУКЕТЫ (первые 70 для проверки):")
print("=" * 80)

for idx, flower in enumerate(all_bouquets[:70], 1):
    image_name = flower.image.name if flower.image else "Нет"
    print(f"{idx:3d}. {flower.name:50s} | Изображение: {image_name[:50]}")
