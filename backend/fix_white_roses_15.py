"""Исправление изображения 'Белые розы (15 шт)' - ТОЛЬКО белые розы, без смешанных"""

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
    logger.info("ИСПРАВЛЕНИЕ 'Белые розы (15 шт)' - ТОЛЬКО БЕЛЫЕ РОЗЫ")
    logger.info("=" * 80)

    # Находим цветок
    flower = Flower.objects.filter(
        Q(name__icontains="Белые розы") & Q(name__icontains="15 шт")
    ).first()

    if not flower:
        logger.error("✗ Цветок 'Белые розы (15 шт)' не найден!")
        sys.exit(1)

    logger.info(f"Найден цветок: {flower.name} (ID: {flower.id})")

    # Используем skip_index чтобы получить ДРУГОЕ изображение (не сушеные розы
    # с запиской)
    search_query = "white roses bouquet fresh"
    logger.info(
        f"Поиск: '{search_query}' (пропуск первых 5 результатов для разнообразия)"
    )

    try:
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        params = {"query": search_query, "per_page": 30, "orientation": "landscape"}
        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Пропускаем первые 5 результатов, чтобы избежать сушеных роз с запиской
                results = (
                    data["results"][5:] if len(data["results"]) > 5 else data["results"]
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

                    score = 0

                    # ОБЯЗАТЕЛЬНО должны быть розы
                    if "rose" in all_text or "roses" in all_text:
                        score += 100
                    else:
                        continue

                    # ОБЯЗАТЕЛЬНО должен быть белый цвет
                    if "white" in all_text:
                        score += 50
                    if "cream" in all_text or "ivory" in all_text:
                        score += 25

                    # СИЛЬНЫЙ штраф за другие цвета (розовый, оранжевый, красный)
                    if "pink" in all_text and "white" not in all_text:
                        score -= 200
                    if "fuchsia" in all_text:
                        score -= 200
                    if "orange" in all_text or "coral" in all_text:
                        score -= 200
                    if "red" in all_text and "white" not in all_text:
                        score -= 200
                    if "yellow" in all_text and "white" not in all_text:
                        score -= 150

                    # Штраф за смешанные букеты
                    if "mixed" in all_text:
                        score -= 200

                    # Штраф за сушеные розы и записки
                    if "dried" in all_text or "dry" in all_text:
                        score -= 200
                    if "note" in all_text or "paper" in all_text or "text" in all_text:
                        score -= 200

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                if (
                    best_photo and best_score >= 100
                ):  # Высокий порог - должны быть розы И белый цвет
                    image_url = best_photo.get("urls", {}).get(
                        "regular"
                    ) or best_photo.get("urls", {}).get("small")
                    logger.info(
                        f"✓ Найдено изображение (score: {best_score}): {image_url[:80]}..."
                    )
                else:
                    logger.error("✗ Не найдено подходящего изображения")
                    sys.exit(1)
            else:
                logger.error("✗ Нет результатов")
                sys.exit(1)
        else:
            logger.error(f"✗ Ошибка API: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Ошибка при запросе: {e}")
        sys.exit(1)

    if not image_url:
        logger.error("✗ Не удалось найти изображение белых роз")
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
