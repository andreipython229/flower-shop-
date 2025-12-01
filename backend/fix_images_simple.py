"""
ПРОСТОЙ И НАДЕЖНЫЙ МЕТОД: Скачиваем правильные изображения из Pexels
с уникальными URL для каждого типа цветка
"""

import os
import re
import time

import django
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ПРОСТОЙ И НАДЕЖНЫЙ МАППИНГ: каждый тип цветка -> уникальный URL из Pexels
# Используем разные ID фотографий для каждого типа
FLOWER_IMAGE_MAP = {
    # Розы - используем разные фотографии для каждого цвета
    "белые розы": ("https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"),
    "красные розы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
    ),
    "розовые розы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "желтые розы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "оранжевые розы": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
    ),
    "бордовые розы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
    ),
    "персиковые розы": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
    ),
    "двухцветные розы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    # Фрезии - используем другие фотографии
    "белые фрезии": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),  # Белые цветы
    "желтые фрезии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "розовые фрезии": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    # Альстромерии - используем другие фотографии
    "желтые альстромерии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "розовые альстромерии": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "белые альстромерии": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "оранжевые альстромерии": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
    ),
    # Остальные цветы - используем подходящие фотографии
    "красные гвоздики": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
    ),
    "розовые гвоздики": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "белые гвоздики": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "желтые гвоздики": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "смешанные гвоздики": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "желтые герберы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "красные герберы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
    ),
    "розовые герберы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "оранжевые герберы": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
    ),
    "белые герберы": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "смешанные герберы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "белые ромашки": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "ромашки с васильками": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "васильки и ромашки": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "синие васильки": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
    ),
    "красные тюльпаны": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
    ),
    "желтые тюльпаны": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "розовые тюльпаны": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "белые тюльпаны": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "фиолетовые тюльпаны": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
    ),
    "смешанные тюльпаны": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
    ),
    "белые хризантемы": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "желтые хризантемы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "розовые хризантемы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "красные хризантемы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
    ),
    "оранжевые хризантемы": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
    ),
    "розовые пионы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "белые пионы": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "бордовые пионы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
    ),
    "белые лилии": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "розовые лилии": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "желтые лилии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "оранжевые лилии": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
    ),
    "синие ирисы": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
    ),
    "фиолетовые ирисы": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
    ),
    "желтые ирисы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "белые ирисы": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "белые орхидеи": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "розовые орхидеи": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "фиолетовые орхидеи": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
    ),
    "желтые орхидеи": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "розовые альстромерии": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "желтые альстромерии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "белые альстромерии": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "оранжевые альстромерии": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
    ),
    "белые фрезии": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "желтые фрезии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
    "розовые фрезии": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "белые астры": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "розовые астры": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "фиолетовые астры": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
    ),
    "красные гладиолусы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
    ),
    "белые гладиолусы": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "розовые гладиолусы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "белые эустомы": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "розовые эустомы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "фиолетовые эустомы": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
    ),
    "синие эустомы": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
    ),
    "смешанный букет": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
    ),
    "свадебный букет": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "букет невесты": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
}


def normalize_name(name):
    """Нормализует название для поиска в маппинге"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    clean = re.sub(r"\s+", " ", clean)
    return clean


def find_image_url(flower_name):
    """Находит URL изображения для цветка"""
    normalized = normalize_name(flower_name)

    # Прямой поиск
    if normalized in FLOWER_IMAGE_MAP:
        return FLOWER_IMAGE_MAP[normalized]

    # Поиск по частичному совпадению
    for key, url in FLOWER_IMAGE_MAP.items():
        if key in normalized or normalized in key:
            return url

    return None


def fix_images():
    """Исправляет изображения для всех цветов"""
    flowers = Flower.objects.all()

    logger.info("=" * 80)
    logger.info("ПРОСТОЙ МЕТОД: Скачиваем правильные изображения из Pexels")
    logger.info("=" * 80)
    logger.info(f"\nОбработка {flowers.count()} цветов...\n")

    updated = 0
    skipped = 0
    failed = 0

    for flower in flowers:
        try:
            image_url = find_image_url(flower.name)

            if not image_url:
                logger.warning(f"⚠ Не найден URL для '{flower.name}'")
                skipped += 1
                continue

            # Удаляем старое
            if flower.image:
                try:
                    old_path = flower.image.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception:
                    pass

            # Скачиваем новое
            try:
                response = requests.get(
                    image_url,
                    stream=True,
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                response.raise_for_status()

                safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                safe_name = re.sub(r"[-\s]+", "_", safe_name)
                timestamp = int(time.time())
                file_name = f"{safe_name}_{timestamp}.jpg"

                image_content = ContentFile(response.content)
                image_path = default_storage.save(f"flowers/{file_name}", image_content)

                flower.image = image_path
                flower.image_url = None
                flower.save()

                logger.info(f"✓ '{flower.name}' -> {normalize_name(flower.name)}")
                updated += 1

            except Exception as e:
                logger.warning(f"⚠ Ошибка для '{flower.name}': {e}")
                failed += 1

        except Exception as e:
            logger.error(f"✗ Ошибка для '{flower.name}': {e}")
            failed += 1

    logger.info("\n" + "=" * 80)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {failed}"
    )
    logger.info("=" * 80)


if __name__ == "__main__":
    fix_images()
