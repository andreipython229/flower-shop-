"""Проверка и исправление изображений розовых гвоздик"""

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

# Сначала проверяем текущие изображения
logger.info("=" * 80)
logger.info("ПРОВЕРКА ТЕКУЩИХ ИЗОБРАЖЕНИЙ")
logger.info("=" * 80)

f25 = Flower.objects.filter(
    Q(name__icontains="Розовые гвоздики") & Q(name__icontains="25 шт")
).first()
f15 = Flower.objects.filter(
    Q(name__icontains="Розовые гвоздики") & Q(name__icontains="15 шт")
).first()

if f25:
    logger.info(f"25 шт (ID {f25.id}): {f25.image.name if f25.image else 'Нет'}")
if f15:
    logger.info(f"15 шт (ID {f15.id}): {f15.image.name if f15.image else 'Нет'}")

# Теперь обновляем через Unsplash
if not UNSPLASH_ACCESS_KEY:
    logger.error("✗ UNSPLASH_ACCESS_KEY не установлен!")
    sys.exit(1)


def get_unsplash_image(search_query, api_key, skip_index=0):
    """Получает изображение из Unsplash API"""
    if not api_key:
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}
        params = {"query": search_query, "per_page": 10, "orientation": "landscape"}
        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                results = (
                    data["results"][skip_index:]
                    if skip_index < len(data["results"])
                    else data["results"]
                )

                for photo in results:
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

                    # Проверяем, что это гвоздики
                    if "carnation" in all_text or "dianthus" in all_text:
                        if "pink" in all_text and "rose" not in all_text:
                            image_url = photo.get("urls", {}).get(
                                "regular"
                            ) or photo.get("urls", {}).get("small")
                            return image_url

                # Если не нашли идеальное, берем первое
                photo = results[0]
                return photo.get("urls", {}).get("regular") or photo.get(
                    "urls", {}
                ).get("small")
        return None
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return None


def update_flower(flower, skip_index=0):
    """Обновляет изображение цветка"""
    if not flower:
        return False

    logger.info(f"\nОбновление: {flower.name} (ID: {flower.id})")

    image_url = get_unsplash_image(
        "pink carnation flowers bouquet", UNSPLASH_ACCESS_KEY, skip_index
    )
    if not image_url:
        logger.warning("  ⚠ Не удалось получить изображение")
        return False

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


logger.info("\n" + "=" * 80)
logger.info("ОБНОВЛЕНИЕ ИЗОБРАЖЕНИЙ")
logger.info("=" * 80)

if f25:
    update_flower(f25, skip_index=0)
    time.sleep(1)

if f15:
    update_flower(f15, skip_index=2)

logger.info("\n" + "=" * 80)
logger.info("✅ ГОТОВО! Обнови страницу в браузере (Ctrl+F5)")
logger.info("=" * 80)
