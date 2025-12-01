"""Исправление изображения 'Белые лилии (3 шт)' для картинки 75 - отличное от картинок 73 и 74"""

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
    logger.info(
        "ИСПРАВЛЕНИЕ 'Белые лилии (3 шт)' ДЛЯ КАРТИНКИ 75 - ОТЛИЧНОЕ ОТ 73 И 74"
    )
    logger.info("=" * 80)

    # Находим "Белые лилии (3 шт)" - картинка 75
    flower = Flower.objects.filter(
        Q(name__icontains="Белые лилии") & Q(name__icontains="3 шт")
    ).first()

    if not flower:
        logger.error("✗ Цветок 'Белые лилии (3 шт)' не найден!")
        sys.exit(1)

    logger.info(f"Найден цветок: {flower.name} (ID: {flower.id})")

    # Используем skip_index=10 чтобы получить ТРЕТЬЕ уникальное изображение
    # 73 использует skip_index=0, 74 использует skip_index=3, 75 использует
    # skip_index=10
    search_query = "white lilies bouquet"
    logger.info(
        f"Поиск: '{search_query}' (пропуск первых 10 результатов для разнообразия)"
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
                # Пропускаем первые 10 результатов для разнообразия
                results = (
                    data["results"][10:]
                    if len(data["results"]) > 10
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

                    score = 50  # Базовый балл - запрос уже содержит "white lilies"

                    # Бонус за упоминание лилий в метаданных
                    if "lily" in all_text or "lilies" in all_text:
                        score += 50

                    # Бонус за белый цвет
                    if "white" in all_text:
                        score += 30
                    if "cream" in all_text or "ivory" in all_text:
                        score += 15

                    # СИЛЬНЫЙ штраф за другие цвета
                    if "purple" in all_text or "violet" in all_text:
                        score -= 200
                    if "blue" in all_text:
                        score -= 200
                    if "pink" in all_text and "white" not in all_text:
                        score -= 200
                    if "red" in all_text and "white" not in all_text:
                        score -= 150
                    if "yellow" in all_text and "white" not in all_text:
                        score -= 150

                    # Штраф за смешанные букеты
                    if "mixed" in all_text:
                        score -= 200

                    # Штраф за другие предметы (конверты, камеры)
                    if (
                        "envelope" in all_text
                        or "camera" in all_text
                        or "note" in all_text
                    ):
                        score -= 200

                    # Штраф за неправильные цветы
                    if "rose" in all_text or "carnation" in all_text:
                        score -= 200

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                if best_photo and best_score >= 50:
                    image_url = best_photo.get("urls", {}).get(
                        "regular"
                    ) or best_photo.get("urls", {}).get("small")
                    logger.info(
                        f"✓ Найдено изображение (score: {best_score}): {image_url[:80]}..."
                    )
                else:
                    logger.error(
                        f"✗ Не найдено подходящего изображения (лучший score: {best_score})"
                    )
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
