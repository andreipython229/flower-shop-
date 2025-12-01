"""
Скрипт для привязки существующих изображений из media/flowers/ к цветам в базе данных
"""

import os
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.conf import settings

from flowers.models import Flower


def assign_existing_images():
    """Привязывает существующие изображения к цветам по названию"""
    media_root = Path(settings.MEDIA_ROOT)
    flowers_dir = media_root / "flowers"

    if not flowers_dir.exists():
        print(f"❌ Папка {flowers_dir} не существует!")
        return

    # Получаем все файлы изображений
    image_files = (
        list(flowers_dir.glob("*.jpg"))
        + list(flowers_dir.glob("*.jpeg"))
        + list(flowers_dir.glob("*.png"))
    )

    print(f"Найдено {len(image_files)} файлов изображений")
    print(f"Всего цветов в базе: {Flower.objects.count()}")
    print("=" * 60)

    updated = 0
    failed = 0

    # Для каждого цветка пытаемся найти подходящее изображение
    for flower in Flower.objects.all():
        if flower.image:  # Если уже есть изображение, пропускаем
            continue

        # Ищем файл, который содержит часть названия цветка
        flower_name_clean = (
            flower.name.lower()
            .replace("(", "")
            .replace(")", "")
            .replace("шт", "")
            .strip()
        )
        flower_name_parts = flower_name_clean.split()

        # Пробуем найти файл по названию
        found_image = None
        for image_file in image_files:
            image_name_lower = image_file.stem.lower()

            # Проверяем, содержит ли имя файла ключевые слова из названия цветка
            if any(
                part in image_name_lower for part in flower_name_parts if len(part) > 3
            ):
                found_image = image_file
                break

        # Если не нашли по названию, берем любое изображение (для разнообразия
        # используем хеш)
        if not found_image and image_files:
            import hashlib

            flower_hash = int(
                hashlib.md5(flower.name.encode("utf-8")).hexdigest()[:8], 16
            )
            found_image = image_files[flower_hash % len(image_files)]

        if found_image:
            # Сохраняем относительный путь
            relative_path = f"flowers/{found_image.name}"
            flower.image = relative_path
            flower.save()
            print(f"✓ Привязано изображение для '{flower.name}': {found_image.name}")
            updated += 1
        else:
            print(f"⚠ Не найдено изображение для '{flower.name}'")
            failed += 1

    print("=" * 60)
    print(f"Готово! Обновлено: {updated}, Не найдено: {failed}")


if __name__ == "__main__":
    assign_existing_images()
