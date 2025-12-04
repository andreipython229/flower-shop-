"""Исправление изображения 'Розовые герберы (9 шт)' для картинки 109"""

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


def get_unsplash_image(search_query, api_key, skip_index=0):
    """Получить изображение из Unsplash API"""
    try:
        headers = {"Authorization": f"Client-ID {api_key}"}
        params = {"query": search_query, "per_page": 30, "orientation": "landscape"}
        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Пропускаем первые результаты для разнообразия
                results = (
                    data["results"][skip_index:]
                    if len(data["results"]) > skip_index
                    else data["results"]
                )

                best_photo = None
                best_score = 0

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

                    score = 50  # Базовый балл

                    # Бонус за упоминание гербер
                    if "gerbera" in all_text or "gerber" in all_text:
                        score += 50

                    # ОБЯЗАТЕЛЬНО должен быть розовый цвет
                    if "pink" in all_text:
                        score += 50
                    if "rose" in all_text and "pink" in all_text:
                        score += 25

                    # СИЛЬНЫЙ штраф за другие цвета
                    if "orange" in all_text:
                        score -= 200
                    if "purple" in all_text and "pink" not in all_text:
                        score -= 200
                    if "red" in all_text and "pink" not in all_text:
                        score -= 150
                    if "yellow" in all_text and "pink" not in all_text:
                        score -= 150
                    if "white" in all_text and "pink" not in all_text:
                        score -= 100

                    # Штраф за смешанные букеты
                    if "mixed" in all_text:
                        score -= 200

                    # Штраф за неправильные цветы
                    if "rose" in all_text and "gerbera" not in all_text:
                        score -= 100
                    if "carnation" in all_text:
                        score -= 200

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                if best_photo and best_score >= 50:
                    image_url = best_photo.get("urls", {}).get(
                        "regular"
                    ) or best_photo.get("urls", {}).get("small")
                    return image_url
                else:
                    logger.warning(
                        f"⚠ Не найдено подходящего изображения "
                        f"(лучший score: {best_score})"
                    )
                    return None
            else:
                logger.warning("⚠ Нет результатов")
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
    logger.info("ИСПРАВЛЕНИЕ 'Розовые герберы (9 шт)' ДЛЯ КАРТИНКИ 109")
    logger.info("=" * 80)

    # Находим "Розовые герберы (9 шт)" - картинка 109
    flower = Flower.objects.filter(
        Q(name__icontains="Розовые герберы") & Q(name__icontains="9 шт")
    ).first()

    if not flower:
        logger.error("✗ Цветок 'Розовые герберы (9 шт)' не найден!")
        sys.exit(1)

    logger.info(f"Найден цветок: {flower.name} (ID: {flower.id})")

    search_query = "pink gerbera flowers bouquet"
    logger.info(f"Поиск: '{search_query}'")

    image_url = get_unsplash_image(search_query, UNSPLASH_ACCESS_KEY, skip_index=0)

    if not image_url:
        logger.error("✗ Не удалось получить изображение из Unsplash")
        sys.exit(1)

    logger.info(f"✓ Найдено изображение: {image_url[:80]}...")

    # Удаляем старое изображение
    if flower.image:
        try:
            if os.path.exists(flower.image.path):
                default_storage.delete(flower.image.name)
                logger.info("  🗑️ Старое изображение удалено")
        except Exception as e:
            logger.warning(f"  ⚠ Не удалось удалить старое изображение: {e}")

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
        logger.info("=" * 80)
        logger.info("✅ ГОТОВО! Обнови страницу в браузере (Ctrl+F5)")
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"✗ Ошибка при загрузке: {e}")
        sys.exit(1)
