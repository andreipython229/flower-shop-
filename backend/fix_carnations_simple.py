"""
Простой скрипт для исправления картинок 118, 119, 120, 121
Использует прямые запросы без сложных проверок
"""

import os
import sys
import time

import django
import requests
from django.core.files.base import ContentFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging

from django.db.models import Q

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def get_unsplash_image(search_query, api_key):
    """Получает первое изображение из Unsplash API по запросу"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        params = {
            "query": search_query,
            "per_page": 1,  # Берем первое изображение
            "orientation": "landscape",
        }

        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                photo = data["results"][0]
                image_url = photo.get("urls", {}).get("regular")
                logger.info("  ✓ Найдено изображение")
                return image_url
            else:
                logger.warning(f"  ⚠ Нет результатов для запроса: '{search_query}'")
                return None
        else:
            logger.error(f"✗ Ошибка API: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"✗ Ошибка при запросе: {e}")
        return None


if __name__ == "__main__":
    if not UNSPLASH_ACCESS_KEY:
        logger.error("✗ UNSPLASH_ACCESS_KEY не установлен!")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("ИСПРАВЛЕНИЕ КАРТИНОК 118, 119, 120, 121 - ПРОСТОЙ ПОДХОД")
    logger.info("=" * 80)
    logger.info("118-119: Белые гвоздики")
    logger.info("120-121: Розовые гвоздики")
    logger.info("")

    # Список букетов для исправления
    flowers_to_fix = [
        {
            "name_part": "Белые гвоздики",
            "count": "25 шт",
            "query": "white carnation bouquet",
        },
        {
            "name_part": "Белые гвоздики",
            "count": "15 шт",
            "query": "white carnation bouquet",
        },
        {
            "name_part": "Розовые гвоздики",
            "count": "25 шт",
            "query": "pink carnation bouquet",
        },
        {
            "name_part": "Розовые гвоздики",
            "count": "15 шт",
            "query": "pink carnation bouquet",
        },
    ]

    updated = 0
    skipped = 0

    for flower_info in flowers_to_fix:
        logger.info("-" * 80)
        logger.info(f"Ищем: {flower_info['name_part']} ({flower_info['count']})")

        # Ищем конкретный букет
        flowers = Flower.objects.filter(
            Q(name__icontains=flower_info["name_part"])
            & Q(name__icontains=flower_info["count"]),
            in_stock=True,
        )

        if not flowers.exists():
            logger.warning(
                f"  ⚠ Не найдено: {flower_info['name_part']} ({flower_info['count']})"
            )
            skipped += 1
            continue

        for flower in flowers:
            logger.info(f"  Обрабатываем: '{flower.name}' (ID: {flower.id})")
            logger.info(f"  Поиск: '{flower_info['query']}'")

            image_url = get_unsplash_image(flower_info["query"], UNSPLASH_ACCESS_KEY)

            if image_url:
                try:
                    # Скачиваем изображение
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        # Генерируем уникальное имя файла
                        timestamp = int(time.time())
                        safe_name = (
                            flower.name.replace(" ", "_")
                            .replace("(", "")
                            .replace(")", "")
                            .replace('"', "")
                            .replace("/", "_")
                        )
                        filename = f"flowers/{safe_name}_{timestamp}.jpg"

                        # Удаляем старое изображение
                        if flower.image:
                            try:
                                old_path = flower.image.path
                                if os.path.exists(old_path):
                                    os.remove(old_path)
                                    logger.info("  ✓ Старое изображение удалено")
                            except Exception as e:
                                logger.warning(
                                    f"  ⚠ Не удалось удалить старое изображение: {e}"
                                )

                        # Сохраняем новое изображение
                        flower.image.save(
                            filename, ContentFile(img_response.content), save=True
                        )
                        logger.info(f"  ✅ Изображение сохранено: {filename}")
                        updated += 1

                        # Небольшая задержка между запросами
                        time.sleep(0.5)
                    else:
                        logger.warning(
                            f"  ⚠ Не удалось скачать изображение: {
        img_response.status_code}"
                        )
                        skipped += 1
                except Exception as e:
                    logger.error(f"  ✗ Ошибка при сохранении: {e}")
                    skipped += 1
            else:
                logger.warning("  ⚠ Не удалось получить изображение")
                skipped += 1

            logger.info("")

    logger.info("=" * 80)
    logger.info(f"Завершено! Обновлено: {updated}, Пропущено: {skipped}")
    logger.info("=" * 80)
    if updated > 0:
        logger.info("✅ Картинки должны теперь показывать правильные гвоздики!")
    logger.info("=" * 80)
