"""
Проверка реальных файлов изображений - что в них на самом деле
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

print("=" * 80)
print("ПРОВЕРКА РЕАЛЬНЫХ ФАЙЛОВ ИЗОБРАЖЕНИЙ")
print("=" * 80)

# Проверяем первые 4 цветка, которые были проблемными
test_flowers = [
    "Белые розы (35 шт)",
    "Красные розы (35 шт)",
    "Белые фрезии (25 шт)",
    "Желтые альстромерии (25 шт)",
]

for flower_name in test_flowers:
    try:
        flower = Flower.objects.get(name=flower_name)
        print(f"\n{flower_name}:")

        if flower.image:
            file_path = flower.image.path
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

            print(f"  Файл: {file_name}")
            print(f"  Размер: {file_size:,} байт")
            print(f"  Путь: {file_path}")

            # Проверяем, есть ли другие цветы с таким же файлом
            same_file_count = Flower.objects.filter(image=flower.image).count()
            if same_file_count > 1:
                print(
                    f"  ⚠ ВНИМАНИЕ: Этот файл используется "
                    f"для {same_file_count} цветов!"
                )
                same_flowers = Flower.objects.filter(image=flower.image).exclude(
                    id=flower.id
                )
                print(
                    f"     Также используется для: "
                    f"{', '.join([f.name for f in same_flowers[:3]])}"
                )
        else:
            print("  ✗ Нет изображения")

    except Flower.DoesNotExist:
        print(f"\n{flower_name}: ✗ Не найден в базе")
    except Exception as e:
        print(f"\n{flower_name}: ✗ Ошибка - {e}")

print("\n" + "=" * 80)
print("ПРОВЕРКА ДУБЛИКАТОВ (цветы с одинаковыми файлами)")
print("=" * 80)

# Находим цветы с одинаковыми файлами
from django.db.models import Count

duplicates = (
    Flower.objects.filter(image__isnull=False)
    .values("image")
    .annotate(count=Count("id"))
    .filter(count__gt=1)
    .order_by("-count")
)

if duplicates:
    print(
        f"\nНайдено {len(duplicates)} файлов, "
        f"которые используются для нескольких цветов:\n"
    )
    for dup in duplicates[:10]:
        flowers_with_same = Flower.objects.filter(image=dup["image"])
        print(f"  Файл: {os.path.basename(flowers_with_same.first().image.path)}")
        print(f"  Используется для {dup['count']} цветов:")
        for f in flowers_with_same:
            print(f"    - {f.name}")
        print()
else:
    print("\n✓ Все цветы имеют уникальные файлы изображений")

print("=" * 80)
