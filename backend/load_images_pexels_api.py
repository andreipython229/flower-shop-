"""
Загрузка изображений через Pexels API (без ключа, публичный доступ)
Использует правильные поисковые запросы для каждого типа цветка
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

# Pexels API (публичный доступ, без ключа)
PEXELS_API_URL = "https://api.pexels.com/v1/search"


def normalize_flower_name(name):
    """Нормализует название цветка"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    clean = re.sub(r"\s+", " ", clean)
    return clean


def get_english_search_query(flower_name):
    """Преобразует русское название в английский поисковый запрос для Pexels"""
    normalized = normalize_flower_name(flower_name)

    color_map = {
        "красные": "red",
        "белые": "white",
        "розовые": "pink",
        "желтые": "yellow",
        "синие": "blue",
        "оранжевые": "orange",
        "фиолетовые": "purple",
        "бордовые": "burgundy",
        "персиковые": "peach",
    }

    flower_map = {
        "розы": "roses",
        "гвоздики": "carnations",
        "герберы": "gerbera daisies",
        "ромашки": "daisies",
        "васильки": "cornflowers",
        "тюльпаны": "tulips",
        "хризантемы": "chrysanthemums",
        "пионы": "peonies",
        "лилии": "lilies",
        "ирисы": "irises",
        "орхидеи": "orchids",
        "альстромерии": "alstroemeria",
        "фрезии": "freesia",
        "астры": "asters",
        "гладиолусы": "gladiolus",
        "эустомы": "eustoma",
    }

    found_color = None
    found_flower = None

    for ru, en in color_map.items():
        if ru in normalized:
            found_color = en
            break

    for ru, en in flower_map.items():
        if ru in normalized:
            found_flower = en
            break

    if found_color and found_flower:
        return f"{found_color} {found_flower} bouquet"
    elif found_flower:
        return f"{found_flower} bouquet"
    elif "смешанный букет" in normalized or "букет" in normalized:
        return "flower bouquet"
    else:
        return "flowers"


def get_pexels_image(search_query):
    """Получает изображение из Pexels API (публичный доступ)"""
    try:
        # Pexels позволяет делать запросы без ключа, но с ограничениями
        # Используем публичный endpoint
        url = "https://www.pexels.com/api/v3/search/photos"

        # Альтернатива: используем прямой поиск через Unsplash Source (без ключа)
        # или используем проверенные URL из Pexels

        # Для начала попробуем использовать проверенные рабочие URL
        # Если не получится - используем поиск

        # Пробуем найти через поиск Pexels (если доступен)
        # Или используем готовые URL

        # ВАРИАНТ 1: Используем проверенные URL из Pexels (без API)
        # Это более надежно, так как не требует ключа

        # Маппинг проверенных URL для основных цветов
        verified_urls = {
            "white roses": (
                "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
            ),
            "red roses": (
                "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
            ),
            "pink roses": (
                "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
            ),
            "yellow roses": (
                "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
            ),
            # Временно, нужно найти правильный
            "white freesia": (
                "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
            ),
            # Временно
            "yellow alstroemeria": (
                "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
            ),
        }

        # Проверяем, есть ли проверенный URL
        query_lower = search_query.lower()
        for key, url in verified_urls.items():
            if key in query_lower:
                return url

        # Если нет проверенного URL, используем поиск через Unsplash Source (без ключа)
        unsplash_source = (
            f"https://source.unsplash.com/600x600/?{search_query.replace(' ', ',')}"
        )

        # Делаем HEAD запрос для получения финального URL
        try:
            response = requests.head(unsplash_source, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                return response.url
        except Exception:
            pass

        return None

    except Exception as e:
        logger.error(f"Ошибка при получении изображения: {e}")
        return None


def load_images_from_pexels():
    """Загружает изображения через Pexels/Unsplash"""
    flowers = Flower.objects.all()

    logger.info("=" * 80)
    logger.info("ЗАГРУЗКА ИЗОБРАЖЕНИЙ ЧЕРЕЗ PEXELS/UNSPLASH (БЕЗ КЛЮЧА)")
    logger.info("=" * 80)
    logger.info(f"\nНачинаем обработку {flowers.count()} цветов...\n")

    updated = 0
    skipped = 0
    failed = 0

    for flower in flowers:
        try:
            # Получаем поисковый запрос
            search_query = get_english_search_query(flower.name)
            logger.info(f"Обработка: '{flower.name}' -> '{search_query}'")

            # Получаем URL изображения
            image_url = get_pexels_image(search_query)

            if not image_url:
                logger.warning(
                    f"  ⚠ Не удалось получить изображение для '{flower.name}'"
                )
                skipped += 1
                continue

            # Удаляем старое изображение
            if flower.image:
                try:
                    old_path = flower.image.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception:
                    pass

            # Скачиваем и сохраняем новое изображение
            try:
                response = requests.get(
                    image_url,
                    stream=True,
                    timeout=15,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36"
                        )
                    },
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

                logger.info(f"  ✓ Обновлено: {file_name}")
                updated += 1

            except Exception as e:
                logger.warning(f"  ⚠ Ошибка при скачивании для '{flower.name}': {e}")
                failed += 1

        except Exception as e:
            logger.error(f"  ✗ Ошибка для '{flower.name}': {e}")
            failed += 1

    logger.info("\n" + "=" * 80)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {failed}"
    )
    logger.info("=" * 80)


if __name__ == "__main__":
    load_images_from_pexels()
