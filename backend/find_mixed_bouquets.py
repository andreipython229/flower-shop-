"""
Скрипт для поиска смешанных букетов, которые показываются на фронтенде
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

# Названия букетов, которые пользователь показал на скриншотах
bouquet_names = [
    'Смешанный букет "Эксклюзив"',
    'Смешанный букет "Классика"',
    'Смешанный букет "Премиум"',
    "Букет невесты",
    "Свадебный букет",
    'Смешанный букет "Осенний"',
    'Смешанный букет "Романтика"',
    'Смешанный букет "Летний"',
    'Смешанный букет "Весенний"',
    'Смешанный букет "Полевой"',
]

print("=" * 80)
print("ПОИСК СМЕШАННЫХ БУКЕТОВ:")
print("=" * 80)

found_flowers = []
for name_pattern in bouquet_names:
    # Ищем по частичному совпадению
    flowers = Flower.objects.filter(
        name__icontains=name_pattern.split('"')[0].strip(), in_stock=True
    )
    for flower in flowers:
        if flower not in found_flowers:
            found_flowers.append(flower)
            image_name = flower.image.name if flower.image else "Нет"
            print(
                f"ID: {flower.id:5d} | {flower.name:60s} | "
                f"Изображение: {image_name[:50]}"
            )

print("")
print(f"Всего найдено: {len(found_flowers)} букетов")

# Проверяем, какие из них имеют одинаковые изображения
print("")
print("=" * 80)
print("ПРОВЕРКА ОДИНАКОВЫХ ИЗОБРАЖЕНИЙ:")
print("=" * 80)

image_groups = {}
for flower in found_flowers:
    if flower.image:
        img_name = flower.image.name
        if img_name not in image_groups:
            image_groups[img_name] = []
        image_groups[img_name].append(flower)

for img_name, flowers_list in image_groups.items():
    if len(flowers_list) > 1:
        print(f"\nОдинаковое изображение '{img_name[:50]}' используется для:")
        for f in flowers_list:
            print(f"  - ID {f.id}: {f.name}")
