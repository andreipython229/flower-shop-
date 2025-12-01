"""
Проверка дубликатов - используются ли одни и те же файлы для разных цветов
"""

import os
from collections import defaultdict

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

print("=" * 80)
print("ПРОВЕРКА ДУБЛИКАТОВ - ОДИНАКОВЫЕ ФАЙЛЫ ДЛЯ РАЗНЫХ ЦВЕТОВ")
print("=" * 80)

# Группируем цветы по файлам
file_to_flowers = defaultdict(list)

for flower in Flower.objects.all():
    if flower.image:
        file_name = os.path.basename(flower.image.name)
        file_to_flowers[file_name].append(flower.name)

# Находим дубликаты
duplicates = {f: names for f, names in file_to_flowers.items() if len(names) > 1}

if duplicates:
    print(
        f"\n⚠ НАЙДЕНО {
        len(duplicates)} ФАЙЛОВ, КОТОРЫЕ ИСПОЛЬЗУЮТСЯ ДЛЯ НЕСКОЛЬКИХ ЦВЕТОВ:\n"
    )

    for file_name, flower_names in list(duplicates.items())[:10]:
        print(f"Файл: {file_name}")
        print(f"Используется для {len(flower_names)} цветов:")
        for name in flower_names:
            print(f"  - {name}")
        print()
else:
    print("\n✓ Все цветы имеют уникальные файлы")

# Проверяем проблемные цветы
print("=" * 80)
print("ПРОВЕРКА ПРОБЛЕМНЫХ ЦВЕТОВ")
print("=" * 80)

problem_flowers = [
    "Белые розы (35 шт)",
    "Красные розы (35 шт)",
    "Белые фрезии (25 шт)",
    "Желтые альстромерии (25 шт)",
]

for flower_name in problem_flowers:
    try:
        flower = Flower.objects.get(name=flower_name)
        if flower.image:
            file_name = os.path.basename(flower.image.name)
            file_path = flower.image.path

            # Проверяем, используется ли этот файл для других цветов
            same_file_flowers = [
                f.name
                for f in Flower.objects.filter(image=flower.image).exclude(id=flower.id)
            ]

            print(f"\n{flower_name}:")
            print(f"  Файл: {file_name}")
            if same_file_flowers:
                print(
                    f"  ⚠ Этот файл также используется для: {', '.join(same_file_flowers[:3])}"
                )
            else:
                print("  ✓ Уникальный файл")

    except Flower.DoesNotExist:
        print(f"\n{flower_name}: ✗ Не найден")

print("\n" + "=" * 80)
