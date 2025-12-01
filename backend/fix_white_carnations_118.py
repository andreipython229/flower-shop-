"""
Скрипт для исправления картинки 118 - "Белые гвоздики (25 шт)"
Нужно заменить гортензии на настоящие белые гвоздики
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

from django.db.models import Q

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def get_unsplash_image(search_query, api_key):
    """Получает изображение из Unsplash API с СТРОГОЙ проверкой на белые гвоздики"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        params = {
            "query": search_query,
            "per_page": 15,  # Берем много результатов для строгого отбора
            "orientation": "landscape",
        }

        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # СТРОГИЙ отбор: ищем ТОЛЬКО белые гвоздики, НЕ гортензии, НЕ розы
                best_photo = None
                best_score = (
                    -100
                )  # Начинаем с отрицательного, чтобы отсеять неподходящие

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

                    # КРИТИЧЕСКИ ВАЖНО: Должны быть именно гвоздики (carnations)
                    if "carnation" in all_text:
                        score += 30  # Очень большой бонус
                    else:
                        score -= 50  # Огромный штраф, если это не гвоздики

                    # КРИТИЧЕСКИ ВАЖНО: Должен быть белый цвет
                    if "white" in all_text:
                        score += 20
                    else:
                        score -= 30  # Штраф, если не белые

                    # ОГРОМНЫЙ ШТРАФ за гортензии (именно эта проблема на картинке 118)
                    if "hydrangea" in all_text or "гортензия" in all_text.lower():
                        score -= 100  # Максимальный штраф

                    # ОГРОМНЫЙ ШТРАФ за розы
                    if "rose" in all_text and "carnation" not in all_text:
                        score -= 100

                    # Штраф за розовый цвет (нужны белые, не розовые)
                    if "pink" in all_text:
                        score -= 25

                    # Бонус за букет
                    if "bouquet" in all_text:
                        score += 5

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                # Используем изображение ТОЛЬКО если score достаточно высокий (гарантия
                # правильности)
                if best_photo and best_score >= 20:  # Минимальный порог для уверенности
                    image_url = best_photo.get("urls", {}).get("regular")
                    logger.info(
                        f"  ✓ Найдено изображение белых гвоздик (score: {best_score})"
                    )
                    return image_url
                else:
                    logger.warning(
                        f"  ⚠ Не найдено подходящего изображения (лучший score: {best_score} < 20)"
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
    logger.info("ИСПРАВЛЕНИЕ КАРТИНКИ 118 - 'БЕЛЫЕ ГВОЗДИКИ (25 шт)'")
    logger.info("=" * 80)
    logger.info("Проблема: показаны гортензии вместо белых гвоздик")
    logger.info("")

    # Ищем конкретный букет "Белые гвоздики (25 шт)"
    flowers = Flower.objects.filter(
        Q(name__icontains="Белые гвоздики") & Q(name__icontains="25 шт"), in_stock=True
    )

    if not flowers.exists():
        # Если не нашли с "25 шт", ищем все "Белые гвоздики"
        flowers = Flower.objects.filter(name__icontains="Белые гвоздики", in_stock=True)
        logger.warning("⚠ Не найдено точно 'Белые гвоздики (25 шт)', ищем все варианты")

    if not flowers.exists():
        logger.warning("⚠ Не найдено букетов 'Белые гвоздики'!")
        sys.exit(0)

    logger.info(f"Найдено букетов: {flowers.count()}\n")

    updated = 0
    skipped = 0

    for flower in flowers:
        logger.info(f"Обрабатываем: '{flower.name}' (ID: {flower.id})")

        # Используем очень специфичный запрос для белых гвоздик
        search_query = "white carnations bouquet flowers"
        logger.info(f"  Поиск: '{search_query}'")

        image_url = get_unsplash_image(search_query, UNSPLASH_ACCESS_KEY)

        if image_url:
            try:
                # Скачиваем изображение
                img_response = requests.get(image_url, timeout=15)
                if img_response.status_code == 200:
                    # Генерируем уникальное имя файла
                    timestamp = int(time.time())
                    safe_name = "Белые_гвоздики_25_шт"
                    filename = f"flowers/{safe_name}_{timestamp}.jpg"

                    # Удаляем старое изображение
                    if flower.image:
                        try:
                            old_path = flower.image.path
                            if os.path.exists(old_path):
                                os.remove(old_path)
                                logger.info("  ✓ Старое изображение удалено")
                        except Exception as e:
                            logger.warning(
                                f"  ⚠ Не удалось удалить старое изображение: {e}"
                            )

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
    if updated > 0:
        logger.info(
            "✅ Картинка 118 должна теперь показывать белые гвоздики, а не гортензии!"
        )
    logger.info("=" * 80)
