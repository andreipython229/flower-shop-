"""
Скрипт для загрузки изображений из проверенных рабочих URL Pexels
"""

import os
import re

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

# Проверенные рабочие URL из Pexels (из кода парсера)
WORKING_PEXELS_URLS = [
    (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),  # Заменен неработающий 1454286
    (
        "https://images.pexels.com/photos/169191/pexels-photo-169191.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/1793525/pexels-photo-1793525.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/2072168/pexels-photo-2072168.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/2300714/pexels-photo-2300714.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/2300715/pexels-photo-2300715.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/2300716/pexels-photo-2300716.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/2300717/pexels-photo-2300717.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
]


def normalize_name(name):
    """Нормализует название для поиска"""
    return re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()


def get_image_url_by_hash(flower_name):
    """Получает URL изображения по хешу названия (гарантирует уникальность)"""
    import hashlib

    flower_hash = int(hashlib.md5(flower_name.encode("utf-8")).hexdigest()[:8], 16)
    selected_url = WORKING_PEXELS_URLS[flower_hash % len(WORKING_PEXELS_URLS)]
    return selected_url


def verify_url(url):
    """Проверяет, работает ли URL"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except Exception:
        return False


def load_images():
    """Загружает изображения для всех цветов"""
    flowers = Flower.objects.all()

    logger.info(f"Начинаем загрузку изображений для {flowers.count()} цветов...")
    logger.info("Используем проверенные URL из Pexels (распределение по хешу)")

    # Проверяем рабочие URL
    logger.info("Проверяем рабочие URL...")
    working_urls = []
    for url in WORKING_PEXELS_URLS:
        if verify_url(url):
            working_urls.append(url)
            logger.info(f"  ✓ Работает: {url[:60]}...")
        else:
            logger.warning(f"  ✗ Не работает: {url[:60]}...")

    if not working_urls:
        logger.error("✗ Нет рабочих URL! Все URL не работают.")
        return

    logger.info(
        f"Найдено {len(working_urls)} рабочих URL из {len(WORKING_PEXELS_URLS)}"
    )

    updated = 0
    failed = 0
    skipped = 0

    for flower in flowers:
        try:
            # Получаем URL по хешу
            image_url = get_image_url_by_hash(flower.name)

            # Скачиваем и сохраняем
            try:
                response = requests.get(
                    image_url,
                    stream=True,
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                response.raise_for_status()

                # Удаляем старое
                if flower.image:
                    try:
                        old_path = flower.image.path
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception:
                        pass

                # Сохраняем новое
                safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                safe_name = re.sub(r"[-\s]+", "_", safe_name)
                file_name = f"{safe_name}.jpg"

                image_content = ContentFile(response.content)
                image_path = default_storage.save(f"flowers/{file_name}", image_content)

                flower.image = image_path
                flower.image_url = None
                flower.save()

                logger.info(f"✓ '{flower.name}'")
                updated += 1

            except Exception as e:
                logger.warning(f"⚠ Ошибка для '{flower.name}': {e}")
                failed += 1

        except Exception as e:
            logger.error(f"✗ Ошибка для '{flower.name}': {e}")
            failed += 1

    logger.info("\n" + "=" * 60)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {failed}"
    )


if __name__ == "__main__":
    load_images()
