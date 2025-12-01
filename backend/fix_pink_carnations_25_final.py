"""Скрипт для исправления изображения 'Розовые гвоздики (25 шт)' через Unsplash API"""

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


def get_unsplash_image(search_query, api_key):
    """Получает изображение из Unsplash API с очень строгим фильтром для гвоздик"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        params = {
            "query": search_query,
            "per_page": 30,  # Берем много результатов для лучшего выбора
            "orientation": "landscape",
        }

        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Ищем изображение с максимальным совпадением ключевых слов
                best_photo = None
                best_score = 0

                for photo in data["results"]:
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
                        continue  # Пропускаем, если нет упоминания гвоздик

                    # Большой бонус за "carnation"
                    if "carnation" in all_text:
                        score += 20
                    if "dianthus" in all_text:
                        score += 15

                    # Бонус за "pink"
                    if "pink" in all_text:
                        score += 10

                    # Штраф за неправильные цветы
                    if "rose" in all_text or "roses" in all_text:
                        score -= 50  # Огромный штраф за розы
                    if "hydrangea" in all_text:
                        score -= 50
                    if "phlox" in all_text:
                        score -= 50

                    # Штраф за неправильный цвет
                    if "purple" in all_text or "white" in all_text or "red" in all_text:
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
                    logger.warning(
                        "  ⚠ Не найдено подходящего изображения с 'carnation'"
                    )
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


if __name__ == "__main__":
    if not UNSPLASH_ACCESS_KEY:
        logger.error("✗ UNSPLASH_ACCESS_KEY не установлен!")
        logger.error("Установите: $env:UNSPLASH_ACCESS_KEY='ваш_ключ'")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("ИСПРАВЛЕНИЕ 'Розовые гвоздики (25 шт)' ЧЕРЕЗ UNSPLASH API")
    logger.info("=" * 80)

    # Находим цветок
    flower = Flower.objects.filter(
        Q(name__icontains="Розовые гвоздики") & Q(name__icontains="25 шт")
    ).first()

    if not flower:
        logger.error("✗ Цветок 'Розовые гвоздики (25 шт)' не найден!")
        sys.exit(1)

    logger.info(f"Найден цветок: {flower.name} (ID: {flower.id})")

    # Очень специфичный запрос для розовых гвоздик
    search_query = "pink carnation flowers bouquet"
    logger.info(f"Поиск: '{search_query}'")

    image_url = get_unsplash_image(search_query, UNSPLASH_ACCESS_KEY)

    if not image_url:
        logger.error("✗ Не удалось получить изображение из Unsplash")
        sys.exit(1)

    logger.info(f"✓ URL: {image_url[:80]}...")

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
            timeout = 30 + (attempt * 10)  # 30, 40, 50 секунд
            logger.info(
                f"  Попытка {attempt + 1}/{max_retries} (таймаут: {timeout}с)..."
            )
            response = requests.get(image_url, stream=True, timeout=timeout)
            response.raise_for_status()
            break  # Успешно, выходим из цикла
        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout,
        ) as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"  ⚠ Таймаут (попытка {
        attempt + 1}/{max_retries}), повторяю через 2 секунды..."
                )
                time.sleep(2)
            else:
                logger.error(
                    f"✗ Ошибка при загрузке изображения после {max_retries} попыток: {e}"
                )
                sys.exit(1)
        except Exception as e:
            logger.error(f"✗ Ошибка при загрузке изображения: {e}")
            sys.exit(1)

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
        logger.info("=" * 80)
        logger.info("✅ ГОТОВО! Обнови страницу в браузере (Ctrl+F5)")
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"✗ Ошибка при сохранении изображения: {e}")
        sys.exit(1)
