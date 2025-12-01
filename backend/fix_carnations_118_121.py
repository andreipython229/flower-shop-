"""
Скрипт для исправления картинок 118, 119, 120, 121
Строгие проверки для правильных изображений гвоздик
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


def get_unsplash_image(search_query, api_key, required_color="white"):
    """Получает изображение из Unsplash API с ОЧЕНЬ СТРОГИМИ проверками"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        params = {
            "query": search_query,
            "per_page": 20,  # Берем много результатов для строгого отбора
            "orientation": "landscape",
        }

        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # ОЧЕНЬ СТРОГИЙ отбор
                best_photo = None
                best_score = -200  # Начинаем с очень отрицательного

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

                    # КРИТИЧЕСКИ ВАЖНО: Должны быть именно ГВОЗДИКИ (carnations)
                    if "carnation" in all_text:
                        score += 40  # Огромный бонус
                    else:
                        # Не такой большой штраф, если нет упоминания, но может быть в
                        # изображении
                        score -= 20  # Штраф, но не критический

                    # КРИТИЧЕСКИЙ ШТРАФ за флоксы (проблема картинок 118-119)
                    if "phlox" in all_text or "флокс" in all_text.lower():
                        score -= 100  # Максимальный штраф - это не гвоздики!

                    # Проверка цвета
                    if required_color == "white":
                        # Должны быть БЕЛЫЕ гвоздики
                        if "white" in all_text:
                            score += 25
                        else:
                            score -= 15  # Меньший штраф

                        # ШТРАФ за розовый цвет
                        if "pink" in all_text:
                            score -= 40  # Штраф, но не критический

                        # ШТРАФ за гортензии (проблема картинки 118)
                        if "hydrangea" in all_text or "гортензия" in all_text.lower():
                            score -= 60  # Большой штраф

                        # КРИТИЧЕСКИЙ ШТРАФ за флоксы (проблема картинок 118-119)
                        if "phlox" in all_text or "флокс" in all_text.lower():
                            score -= 100  # Максимальный штраф

                    elif required_color == "pink":
                        # Должны быть РОЗОВЫЕ гвоздики
                        if "pink" in all_text:
                            score += 25
                        else:
                            score -= 15  # Меньший штраф

                        # ШТРАФ за оранжевый/красный (проблема картинок 120, 121)
                        if "orange" in all_text or "red" in all_text:
                            if "pink" not in all_text:
                                score -= 40  # Штраф

                        # Штраф за белый цвет
                        if "white" in all_text and "pink" not in all_text:
                            score -= 20

                    # ШТРАФ за розы (не гвоздики!)
                    if "rose" in all_text and "carnation" not in all_text:
                        score -= 50  # Штраф, но не критический

                    # Бонус за букет
                    if "bouquet" in all_text:
                        score += 5

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                # Используем лучшее изображение из доступных
                # Если есть хотя бы одно изображение, используем его
                if best_photo:
                    image_url = best_photo.get("urls", {}).get("regular")
                    logger.info(f"  ✓ Найдено изображение (score: {best_score})")
                    return image_url
                else:
                    # Если не нашли лучшее, берем первое из результатов
                    photo = data["results"][0]
                    image_url = photo.get("urls", {}).get("regular")
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
    logger.info("ИСПРАВЛЕНИЕ КАРТИНОК 118, 119, 120, 121")
    logger.info("=" * 80)
    logger.info("Проблемы:")
    logger.info("  118: Белые гвоздики (25 шт) - показаны гортензии")
    logger.info("  119: Белые гвоздики (15 шт) - показаны розовые гвоздики")
    logger.info("  120: Розовые гвоздики (25 шт) - показаны оранжевые/красные цветы")
    logger.info("  121: Розовые гвоздики (15 шт) - показаны оранжевые/красные цветы")
    logger.info("")

    # Список букетов для исправления
    flowers_to_fix = [
        {"name_part": "Белые гвоздики", "count": "25 шт", "color": "white"},
        {"name_part": "Белые гвоздики", "count": "15 шт", "color": "white"},
        {"name_part": "Розовые гвоздики", "count": "25 шт", "color": "pink"},
        {"name_part": "Розовые гвоздики", "count": "15 шт", "color": "pink"},
    ]

    updated = 0
    skipped = 0

    for flower_info in flowers_to_fix:
        logger.info("-" * 80)
        logger.info(f"Ищем: {flower_info['name_part']} ({flower_info['count']})")

        # Ищем конкретный букет
        flowers = Flower.objects.filter(
            Q(name__icontains=flower_info["name_part"])
            & Q(name__icontains=flower_info["count"]),
            in_stock=True,
        )

        if not flowers.exists():
            logger.warning(
                f"  ⚠ Не найдено: {flower_info['name_part']} ({flower_info['count']})"
            )
            skipped += 1
            continue

        for flower in flowers:
            logger.info(f"  Обрабатываем: '{flower.name}' (ID: {flower.id})")

            # Формируем очень специфичный запрос для правильных гвоздик
            if flower_info["color"] == "white":
                search_query = "white carnation flowers bouquet"
            else:
                search_query = "pink carnation flowers bouquet"

            logger.info(f"  Поиск: '{search_query}'")

            image_url = get_unsplash_image(
                search_query, UNSPLASH_ACCESS_KEY, required_color=flower_info["color"]
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
                            .replace("/", "_")
                        )
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
            "✅ Картинки 118, 119, 120, 121 должны теперь показывать правильные гвоздики!"
        )
    logger.info("=" * 80)
