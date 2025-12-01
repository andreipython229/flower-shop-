"""
Скрипт для исправления изображения "Белые герберы" - сделать более ярким и четким
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

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def get_unsplash_image(search_query, api_key):
    """Получает изображение из Unsplash API с приоритетом на яркие и четкие изображения"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        params = {
            "query": search_query,
            "per_page": 10,  # Берем больше результатов для лучшего выбора
            "orientation": "landscape",
        }

        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Ищем яркое и четкое изображение белых гербер
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

                    # Бонус за упоминание гербер
                    if "gerbera" in all_text or "гербера" in all_text.lower():
                        score += 20  # Очень важный критерий

                    # Бонус за упоминание белого цвета
                    if "white" in all_text:
                        score += 10

                    # Бонус за слова, связанные с яркостью и четкостью
                    if (
                        "bright" in all_text
                        or "vibrant" in all_text
                        or "fresh" in all_text
                    ):
                        score += 8

                    if (
                        "crisp" in all_text
                        or "clear" in all_text
                        or "sharp" in all_text
                    ):
                        score += 5

                    # Бонус за букет
                    if "bouquet" in all_text:
                        score += 5

                    # Штраф за тусклые/размытые изображения
                    if "blur" in all_text or "soft" in all_text or "dim" in all_text:
                        score -= 10

                    # Проверяем качество изображения через размеры (больше = лучше
                    # качество)
                    width = photo.get("width", 0)
                    height = photo.get("height", 0)
                    if width > 2000 and height > 2000:
                        score += 5  # Бонус за высокое разрешение

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                # Используем лучшее изображение
                if best_photo:
                    # Используем 'full' размер для максимального качества
                    image_url = best_photo.get("urls", {}).get(
                        "full"
                    ) or best_photo.get("urls", {}).get("regular")
                    logger.info(
                        f"  ✓ Найдено яркое изображение белых гербер (score: {best_score})"
                    )
                    return image_url
                else:
                    # Если не нашли лучшее, берем первое с максимальным качеством
                    photo = data["results"][0]
                    image_url = photo.get("urls", {}).get("full") or photo.get(
                        "urls", {}
                    ).get("regular")
                    logger.info("  ✓ Использовано первое доступное изображение")
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
    logger.info("ИСПРАВЛЕНИЕ 'БЕЛЫЕ ГЕРБЕРЫ' - ЯРКОЕ ИЗОБРАЖЕНИЕ")
    logger.info("=" * 80)

    # Ищем букет "Белые герберы"
    flowers = Flower.objects.filter(name__icontains="Белые герберы", in_stock=True)

    if not flowers.exists():
        logger.warning("⚠ Не найдено букетов 'Белые герберы'!")
        sys.exit(0)

    logger.info(f"Найдено букетов: {flowers.count()}\n")

    updated = 0

    for flower in flowers:
        logger.info(f"Обрабатываем: '{flower.name}' (ID: {flower.id})")

        # Используем запрос с акцентом на яркость и четкость
        search_query = "bright white gerbera daisy bouquet fresh vibrant"
        logger.info(f"  Поиск: '{search_query}'")

        image_url = get_unsplash_image(search_query, UNSPLASH_ACCESS_KEY)

        if image_url:
            try:
                # Скачиваем изображение
                img_response = requests.get(image_url, timeout=15)
                if img_response.status_code == 200:
                    # Генерируем уникальное имя файла
                    timestamp = int(time.time())
                    safe_name = "Белые_герберы"
                    filename = f"flowers/{safe_name}_{timestamp}.jpg"

                    # Удаляем старое изображение
                    if flower.image:
                        try:
                            old_path = flower.image.path
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        except Exception:
                            pass

                    # Сохраняем новое изображение
                    flower.image.save(
                        filename, ContentFile(img_response.content), save=True
                    )
                    logger.info(f"  ✅ Изображение сохранено: {filename}")
                    updated += 1
                else:
                    logger.warning(
                        f"  ⚠ Не удалось скачать изображение: {
        img_response.status_code}"
                    )
            except Exception as e:
                logger.error(f"  ✗ Ошибка при сохранении: {e}")
        else:
            logger.warning("  ⚠ Не удалось получить изображение")

        logger.info("")

    logger.info("=" * 80)
    logger.info(f"Завершено! Обновлено: {updated}")
    logger.info("=" * 80)
