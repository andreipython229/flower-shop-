import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower
from flowers.parsers import FlowerParser

# Удаляем все существующие цветы
Flower.objects.all().delete()
print("База очищена. Начинаем парсинг цветов через Unsplash API...")

# Используем парсер с Unsplash API
parser = FlowerParser()
flowers_data = parser.parse_flowers()
parser.save_flowers(flowers_data)

print(f"\nВсего цветов в базе: {Flower.objects.count()}")
