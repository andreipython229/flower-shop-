"""
Скрипт для исправления изображений гвоздик (белые и розовые)
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


def get_unsplash_image(search_query, api_key, color_type="white"):
    """Получает изображение из Unsplash API с проверкой на правильный тип цветов"""
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
                # Ищем изображение с правильными гвоздиками
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

                    # ОЧЕНЬ ВАЖНО: Бонус за упоминание гвоздик (carnations)
                    if "carnation" in all_text or "гвоздика" in all_text.lower():
                        score += (
                            25  # Критически важно - это должны быть именно гвоздики
                        )
                    else:
                        score -= 20  # Сильный штраф, если это не гвоздики

                    # Проверка цвета
                    if color_type == "white":
                        # Бонус за белый цвет
                        if "white" in all_text:
                            score += 15
                        # Штраф за розовый цвет (нам нужны белые, не розовые)
                        if "pink" in all_text:
                            score -= 20
                    elif color_type == "pink":
                        # Бонус за розовый цвет
                        if "pink" in all_text:
                            score += 15
                        # Штраф за белый цвет (нам нужны розовые, не белые)
                        if "white" in all_text and "pink" not in all_text:
                            score -= 10

                    # Штраф за другие цветы (розы, гортензии и т.д.)
                    if "rose" in all_text and "carnation" not in all_text:
                        score -= 30  # Очень сильный штраф за розы вместо гвоздик

                    if "hydrangea" in all_text or "гортензия" in all_text.lower():
                        score -= 30  # Сильный штраф за гортензии вместо гвоздик

                    # Бонус за букет
                    if "bouquet" in all_text:
                        score += 5

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                # Используем лучшее изображение только если score положительный
                if best_photo and best_score > 10:  # Минимальный порог для качества
                    image_url = best_photo.get("urls", {}).get("regular")
                    logger.info(
                        f"  ✓ Найдено изображение гвоздик (score: {best_score})"
                    )
                    return image_url
                else:
                    logger.warning(
                        f"  ⚠ Не найдено подходящего изображения "
                        f"(лучший score: {best_score})"
                    )
                    return None
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
    logger.info("ИСПРАВЛЕНИЕ ИЗОБРАЖЕНИЙ ГВОЗДИК")
    logger.info("=" * 80)

    # Ищем все букеты с гвоздиками
    white_carnations = Flower.objects.filter(
        name__icontains="Белые гвоздики", in_stock=True
    )
    pink_carnations = Flower.objects.filter(
        name__icontains="Розовые гвоздики", in_stock=True
    )

    all_flowers = list(white_carnations) + list(pink_carnations)

    if not all_flowers:
        logger.warning("⚠ Не найдено букетов с гвоздиками!")
        sys.exit(0)

    logger.info(f"Найдено букетов: {len(all_flowers)}\n")

    updated = 0
    skipped = 0

    for flower in all_flowers:
        # Определяем тип цвета
        if "белые" in flower.name.lower() or "white" in flower.name.lower():
            color_type = "white"
            search_query = "white carnations bouquet flowers"
        elif "розовые" in flower.name.lower() or "pink" in flower.name.lower():
            color_type = "pink"
            search_query = "pink carnations bouquet flowers"
        else:
            color_type = "white"
            search_query = "carnations bouquet flowers"

        logger.info(f"Обрабатываем: '{flower.name}' (ID: {flower.id})")
        logger.info(f"  Тип: {color_type}, Поиск: '{search_query}'")

        image_url = get_unsplash_image(
            search_query, UNSPLASH_ACCESS_KEY, color_type=color_type
        )

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
                    )
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
