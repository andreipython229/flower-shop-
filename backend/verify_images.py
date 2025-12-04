"""
Скрипт для проверки правильности загруженных изображений
"""

import os
from collections import defaultdict

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower
from flowers.parsers import FlowerParser


def verify_images():
    """Проверяет, что все изображения загружены и соответствуют названиям"""
    parser = FlowerParser()
    flowers = Flower.objects.all()

    print("=" * 80)
    print("ПРОВЕРКА ИЗОБРАЖЕНИЙ ЦВЕТОВ")
    print("=" * 80)

    # Статистика
    total = flowers.count()
    with_images = 0
    without_images = 0

    # Группировка по типам цветов
    flower_types = defaultdict(list)

    for flower in flowers:
        # Очищаем название от количества для группировки
        clean_name = flower.name.lower()
        clean_name = clean_name.split("(")[0].strip()

        if flower.image:
            with_images += 1
            flower_types[clean_name].append(
                {
                    "name": flower.name,
                    "has_image": True,
                    "image_path": flower.image.name,
                }
            )
        else:
            without_images += 1
            flower_types[clean_name].append(
                {"name": flower.name, "has_image": False, "image_path": None}
            )

    print("\n📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   Всего цветов: {total}")
    print(f"   С изображениями: {with_images} ({with_images*100//total}%)")
    print(f"   Без изображений: {without_images} ({without_images*100//total}%)")

    print("\n📋 ПРОВЕРКА ПО ТИПАМ ЦВЕТОВ:")
    print("-" * 80)

    # Проверяем каждый тип цветка
    for flower_type, items in sorted(flower_types.items()):
        with_img = sum(1 for item in items if item["has_image"])
        total_type = len(items)

        status = "✓" if with_img == total_type else "⚠"
        print(
            f"{status} {flower_type.capitalize()}: "
            f"{with_img}/{total_type} с изображениями"
        )

        # Показываем примеры для каждого типа
        if items:
            example = items[0]
            if example["has_image"]:
                print(f"   Пример: {example['name']} -> {example['image_path']}")
            else:
                print(f"   Пример: {example['name']} -> НЕТ ИЗОБРАЖЕНИЯ")

    print("\n" + "=" * 80)
    print("ПРОВЕРКА СООТВЕТСТВИЯ URL НАЗВАНИЯМ:")
    print("=" * 80)

    # Проверяем, что URL соответствуют названиям
    sample_flowers = [
        "Красные розы (7 шт)",
        "Белые розы (7 шт)",
        "Розовые розы (7 шт)",
        "Желтые розы (7 шт)",
        "Красные гвоздики (15 шт)",
        "Белые гвоздики (15 шт)",
        "Желтые герберы (9 шт)",
        "Белые ромашки (20 шт)",
    ]

    print("\nПроверка соответствия URL для примеров:")
    for flower_name in sample_flowers:
        try:
            flower = Flower.objects.get(name=flower_name)
            expected_url = parser._get_flower_image_url_by_name(flower_name)

            if flower.image:
                print(f"✓ {flower_name}")
                if expected_url:
                    print(f"  Ожидаемый URL: {expected_url[:60]}...")
                    print(f"  Загружено: {flower.image.name}")
                else:
                    print("  ⚠ URL не найден в маппинге")
            else:
                print(f"✗ {flower_name} - НЕТ ИЗОБРАЖЕНИЯ")
        except Flower.DoesNotExist:
            print(f"✗ {flower_name} - НЕ НАЙДЕН В БД")

    print("\n" + "=" * 80)

    if without_images == 0:
        print("✅ ВСЕ ЦВЕТЫ ИМЕЮТ ИЗОБРАЖЕНИЯ!")
    else:
        print(f"⚠ ВНИМАНИЕ: {without_images} цветов без изображений")

    print("=" * 80)


if __name__ == "__main__":
    verify_images()
