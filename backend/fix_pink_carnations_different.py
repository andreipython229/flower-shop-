"""Загрузка РАЗНЫХ изображений розовых гвоздик для 25 шт и 15 шт"""

import logging
import os
import sys
import time

import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def get_different_unsplash_images(search_query, api_key, count=2):
    """Получает РАЗНЫЕ изображения из Unsplash API"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return []

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}
        params = {"query": search_query, "per_page": 30, "orientation": "landscape"}
        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                valid_images = []

                for photo in data["results"]:
                    description = (
                        photo.get("description", "").lower()
                        if photo.get("description")
                        else ""
                    )
                    alt_description = (
                        photo.get("alt_description", "").lower()
                        if photo.get("alt_description")
                        else ""
                    )
                    tags = [
                        tag.get("title", "").lower()
                        for tag in photo.get("tags", [])
                        if tag.get("title")
                    ]
                    all_text = f"{description} {alt_description} {' '.join(tags)}"

                    # Строгая проверка: должны быть гвоздики и розовый цвет
                    if (
                        "carnation" in all_text or "dianthus" in all_text
                    ) and "pink" in all_text:
                        if "rose" not in all_text and "hydrangea" not in all_text:
                            image_url = photo.get("urls", {}).get(
                                "regular"
                            ) or photo.get("urls", {}).get("small")
                            image_id = photo.get(
                                "id"
                            )  # Используем ID для проверки уникальности

                            # Проверяем, что это не дубликат
                            if not any(img["id"] == image_id for img in valid_images):
                                valid_images.append({"url": image_url, "id": image_id})

                                if len(valid_images) >= count:
                                    break

                return [img["url"] for img in valid_images]
        return []
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return []


def update_flower(flower, image_url):
    """Обновляет изображение цветка"""
    if not flower or not image_url:
        return False

    logger.info(f"\nОбновление: {flower.name} (ID: {flower.id})")

    # Удаляем старое
    if flower.image:
        try:
            if os.path.exists(flower.image.path):
                default_storage.delete(flower.image.name)
        except Exception:
            pass

    # Загружаем новое
    try:
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()

        import re

        safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip().replace(" ", "_")
        unique_filename = f"flowers/{safe_name}_{int(time.time())}.jpg"

        flower.image.save(unique_filename, ContentFile(response.content), save=False)
        flower.image_url = None
        flower.save()

        logger.info(f"  ✅ Изображение сохранено: {flower.image.name}")
        return True
    except Exception as e:
        logger.error(f"  ✗ Ошибка: {e}")
        return False


if __name__ == "__main__":
    if not UNSPLASH_ACCESS_KEY:
        logger.error("✗ UNSPLASH_ACCESS_KEY не установлен!")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("ЗАГРУЗКА РАЗНЫХ ИЗОБРАЖЕНИЙ РОЗОВЫХ ГВОЗДИК")
    logger.info("=" * 80)

    f25 = Flower.objects.filter(
        Q(name__icontains="Розовые гвоздики") & Q(name__icontains="25 шт")
    ).first()
    f15 = Flower.objects.filter(
        Q(name__icontains="Розовые гвоздики") & Q(name__icontains="15 шт")
    ).first()

    if not f25 or not f15:
        logger.error("✗ Не найдены цветы!")
        sys.exit(1)

    # Получаем ДВА РАЗНЫХ изображения
    logger.info("Поиск разных изображений розовых гвоздик...")
    image_urls = get_different_unsplash_images(
        "pink carnation flowers bouquet", UNSPLASH_ACCESS_KEY, count=2
    )

    if len(image_urls) < 2:
        logger.warning(
            f"⚠ Найдено только {
        len(image_urls)} изображений, попробуем другой запрос..."
        )
        # Пробуем альтернативный запрос
        image_urls = get_different_unsplash_images(
            "pink dianthus bouquet", UNSPLASH_ACCESS_KEY, count=2
        )

    if len(image_urls) < 2:
        logger.error(
            f"✗ Не удалось найти 2 разных изображения (найдено: {len(image_urls)})"
        )
        sys.exit(1)

    logger.info(f"✓ Найдено {len(image_urls)} разных изображений")

    # Обновляем оба цветка РАЗНЫМИ изображениями
    update_flower(f25, image_urls[0])
    time.sleep(1)
    update_flower(f15, image_urls[1])

    logger.info("\n" + "=" * 80)
    logger.info("✅ ГОТОВО! Обнови страницу в браузере (Ctrl+F5)")
    logger.info("=" * 80)
