"""Проверка реальных файлов изображений розовых гвоздик"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.db.models import Q  # noqa: E402

from flowers.models import Flower  # noqa: E402

print("=" * 80)
print("ПРОВЕРКА ИЗОБРАЖЕНИЙ РОЗОВЫХ ГВОЗДИК")
print("=" * 80)

f25 = Flower.objects.filter(
    Q(name__icontains="Розовые гвоздики") & Q(name__icontains="25 шт")
).first()
f15 = Flower.objects.filter(
    Q(name__icontains="Розовые гвоздики") & Q(name__icontains="15 шт")
).first()

for flower in [f25, f15]:
    if not flower:
        continue

    print(f"\n{flower.name} (ID: {flower.id}):")
    if flower.image:
        print(f"  Файл в БД: {flower.image.name}")

        # Проверяем полный путь
        try:
            full_path = flower.image.path
            print(f"  Полный путь: {full_path}")

            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                print(f"  ✓ Файл существует, размер: {file_size:,} байт")
                print(f"  URL: http://localhost:8000{flower.image.url}")
            else:
                print("  ✗ ФАЙЛ НЕ СУЩЕСТВУЕТ!")
        except Exception as e:
            print(f"  ✗ Ошибка при получении пути: {e}")
    else:
        print("  ✗ Нет изображения в БД")

print("\n" + "=" * 80)
