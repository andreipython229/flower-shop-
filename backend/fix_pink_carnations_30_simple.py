"""Простое исправление 'Розовые гвоздики (30 шт)' -
берем первое изображение из Unsplash"""

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

if __name__ == "__main__":
    if not UNSPLASH_ACCESS_KEY:
        logger.error("✗ UNSPLASH_ACCESS_KEY не установлен!")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("ИСПРАВЛЕНИЕ 'Розовые гвоздики (30 шт)' - ПРОСТОЙ ПОДХОД")
    logger.info("=" * 80)

    # Находим цветок
    flower = Flower.objects.filter(
        Q(name__icontains="Розовые гвоздики") & Q(name__icontains="30 шт")
    ).first()

    if not flower:
        logger.error("✗ Цветок 'Розовые гвоздики (30 шт)' не найден!")
        sys.exit(1)

    logger.info(f"Найден цветок: {flower.name} (ID: {flower.id})")

    # Пробуем несколько разных запросов для поиска розовых гвоздик
    search_queries = [
        "pink dianthus caryophyllus",
        "pink carnation dianthus",
        "pink carnation close up",
        "pink carnation bouquet",
    ]

    image_url = None
    for search_query in search_queries:
        logger.info(f"Поиск: '{search_query}'")

        try:
            headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
            params = {"query": search_query, "per_page": 30, "orientation": "landscape"}
            response = requests.get(
                UNSPLASH_API_URL, headers=headers, params=params, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    # Ищем изображение с ОБЯЗАТЕЛЬНЫМ упоминанием "carnation" или
                    # "dianthus"
                    best_photo = None
                    best_score = 0

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

                        score = 0

                        # ОБЯЗАТЕЛЬНО должно быть "carnation" или "dianthus"
                        if "carnation" in all_text:
                            score += 100  # Огромный бонус
                        elif "dianthus" in all_text:
                            score += 80
                        else:
                            continue  # Пропускаем, если нет упоминания гвоздик

                        # Бонус за "pink"
                        if "pink" in all_text:
                            score += 50

                        # Штраф за неправильные цветы
                        if "rose" in all_text or "roses" in all_text:
                            score -= 200  # Огромный штраф
                        if (
                            "peony" in all_text
                            or "lily" in all_text
                            or "tulip" in all_text
                        ):
                            score -= 150

                        if score > best_score:
                            best_score = score
                            best_photo = photo

                    if best_photo and best_score >= 50:
                        image_url = best_photo.get("urls", {}).get(
                            "regular"
                        ) or best_photo.get("urls", {}).get("small")
                        logger.info(
                            f"✓ Найдено изображение (score: {best_score}): "
                            f"{image_url[:80]}..."
                        )
                        break  # Нашли подходящее, выходим из цикла
        except Exception as e:
            logger.warning(f"  ⚠ Ошибка при запросе '{search_query}': {e}")
            continue

    if not image_url:
        logger.error(
            "✗ Не удалось найти изображение розовых гвоздик ни по одному запросу"
        )
        sys.exit(1)

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
