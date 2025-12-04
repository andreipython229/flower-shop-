"""Скрипт для исправления изображений 'Розовые гвоздики (25 шт)' и
'Розовые гвоздики (15 шт)' через Unsplash API"""

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
    """Получает изображение из Unsplash API с очень строгим фильтром
    для розовых гвоздик"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
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
                # Пропускаем первые skip_index результатов для разнообразия
                results = data["results"][skip_index:]
                if not results:
                    results = data["results"]

                set(search_query.lower().split())
                best_photo = None
                best_score = 0

                for photo in results:
                    score = 0
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

                    # ОБЯЗАТЕЛЬНО должно быть слово "carnation" или "dianthus"
                    if "carnation" not in all_text and "dianthus" not in all_text:
                        continue

                    # Большой бонус за "carnation"
                    if "carnation" in all_text:
                        score += 20
                    if "dianthus" in all_text:
                        score += 15

                    # Бонус за "pink"
                    if "pink" in all_text:
                        score += 15

                    # Штраф за неправильные цветы
                    if "rose" in all_text or "roses" in all_text:
                        score -= 50
                    if "hydrangea" in all_text:
                        score -= 50
                    if "phlox" in all_text:
                        score -= 50

                    # Штраф за неправильный цвет
                    if "red" in all_text or "white" in all_text or "purple" in all_text:
                        if "pink" not in all_text:
                            score -= 20

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                if best_photo and best_score > 0:
                    image_url = best_photo.get("urls", {}).get(
                        "regular"
                    ) or best_photo.get("urls", {}).get("small")
                    logger.info(f"  ✓ Найдено изображение (score: {best_score})")
                    return image_url
                else:
                    logger.warning("  ⚠ Не найдено подходящего изображения")
                    return None
            else:
                logger.warning(f"  ⚠ Нет результатов для запроса: '{search_query}'")
                return None
        elif response.status_code == 403:
            logger.error("✗ 403 Forbidden - лимит исчерпан")
            return None
        elif response.status_code == 401:
            logger.error("✗ Unsplash API ключ невалиден (401)")
            return None
        else:
            logger.error(f"✗ Ошибка API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Ошибка при запросе: {e}")
        return None


def update_flower_image(flower, search_query, skip_index=0):
    """Обновляет изображение для цветка"""
    logger.info(
        f"\n'{
        flower.name}' (ID: {
            flower.id}) -> поиск: '{search_query}' (пропуск: {skip_index})"
    )

    image_url = get_unsplash_image(
        search_query, UNSPLASH_ACCESS_KEY, skip_index=skip_index
    )

    if not image_url:
        logger.warning("  ⚠ Не удалось получить изображение")
        return False

    logger.info(f"  ✓ URL: {image_url[:80]}...")

    # Удаляем старое изображение
    if flower.image:
        try:
            if os.path.exists(flower.image.path):
                default_storage.delete(flower.image.name)
                logger.info("  🗑️ Старое изображение удалено")
        except Exception as e:
            logger.warning(f"  ⚠ Не удалось удалить старое изображение: {e}")

    # Загружаем новое изображение с повторными попытками
    max_retries = 3
    for attempt in range(max_retries):
        try:
            timeout = 30 + (attempt * 10)
            response = requests.get(image_url, stream=True, timeout=timeout)
            response.raise_for_status()
            break
        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout,
        ) as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"  ⚠ Таймаут (попытка {attempt + 1}/{max_retries}), повторяю..."
                )
                time.sleep(2)
            else:
                logger.error(f"✗ Ошибка при загрузке изображения: {e}")
                return False
        except Exception as e:
            logger.error(f"✗ Ошибка при загрузке изображения: {e}")
            return False

    try:
        # Генерируем уникальное имя файла
        import re

        safe_flower_name = (
            re.sub(r"[^\w\s-]", "", flower.name).strip().replace(" ", "_")
        )
        unique_filename = f"flowers/{safe_flower_name}_{int(time.time())}.jpg"

        flower.image.save(unique_filename, ContentFile(response.content), save=False)
        flower.image_url = None
        flower.save()

        logger.info(f"  ✅ Изображение сохранено: {flower.image.name}")
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка при сохранении изображения: {e}")
        return False


if __name__ == "__main__":
    if not UNSPLASH_ACCESS_KEY:
        logger.error("✗ UNSPLASH_ACCESS_KEY не установлен!")
        logger.error("Установите: $env:UNSPLASH_ACCESS_KEY='ваш_ключ'")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("ИСПРАВЛЕНИЕ 'Розовые гвоздики (25 шт)' И 'Розовые гвоздики (15 шт)'")
    logger.info("=" * 80)

    # Находим оба цветка
    flower_25 = Flower.objects.filter(
        Q(name__icontains="Розовые гвоздики") & Q(name__icontains="25 шт")
    ).first()
    flower_15 = Flower.objects.filter(
        Q(name__icontains="Розовые гвоздики") & Q(name__icontains="15 шт")
    ).first()

    if not flower_25:
        logger.error("✗ Цветок 'Розовые гвоздики (25 шт)' не найден!")
        sys.exit(1)

    if not flower_15:
        logger.error("✗ Цветок 'Розовые гвоздики (15 шт)' не найден!")
        sys.exit(1)

    logger.info("Найдены цветы:")
    logger.info(f"  - {flower_25.name} (ID: {flower_25.id})")
    logger.info(f"  - {flower_15.name} (ID: {flower_15.id})")

    # Обновляем изображения
    search_query = "pink carnation flowers bouquet"
    updated_25 = update_flower_image(flower_25, search_query, skip_index=0)
    time.sleep(1)  # Задержка между запросами
    updated_15 = update_flower_image(
        flower_15, search_query, skip_index=2
    )  # Пропускаем 2 результата для разнообразия

    logger.info("\n" + "=" * 80)
    if updated_25 and updated_15:
        logger.info(
            "✅ ОБА ИЗОБРАЖЕНИЯ ОБНОВЛЕНЫ! Обнови страницу в браузере (Ctrl+F5)"
        )
    elif updated_25:
        logger.info("⚠ Обновлено только 'Розовые гвоздики (25 шт)'")
    elif updated_15:
        logger.info("⚠ Обновлено только 'Розовые гвоздики (15 шт)'")
    else:
        logger.error("✗ Не удалось обновить изображения")
    logger.info("=" * 80)
