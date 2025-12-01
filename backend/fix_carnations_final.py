"""
Финальный скрипт для исправления картинок 118, 119, 120, 121
Строгая проверка: только гвоздики, без роз и других цветов
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
    """Получает изображение из Unsplash API с проверкой на правильные гвоздики"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        params = {
            "query": search_query,
            "per_page": 30,  # Проверяем еще больше результатов
            "orientation": "landscape",
        }

        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Ищем правильное изображение среди результатов
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

                    # КРИТИЧЕСКОЕ ПРОВЕРКА: Должны быть именно ГВОЗДИКИ
                    # (carnation или dianthus)
                    has_carnation = "carnation" in all_text or "dianthus" in all_text

                    # КРИТИЧЕСКОЕ ПРОВЕРКА: НЕ должны быть розы, гортензии, хризантемы
                    has_rose = "rose" in all_text and "carnation" not in all_text
                    has_hydrangea = (
                        "hydrangea" in all_text or "гортензия" in all_text.lower()
                    )
                    has_chrysanthemum = (
                        "chrysanthemum" in all_text or "хризантема" in all_text.lower()
                    )
                    has_phlox = "phlox" in all_text or "флокс" in all_text.lower()

                    # Проверка цвета
                    if required_color == "white":
                        has_white = "white" in all_text
                        has_yellow = "yellow" in all_text
                        # НЕ должны быть желтые гвоздики, розы, гортензии,
                        # хризантемы, флоксы
                        if (
                            has_carnation
                            and has_white
                            and not has_rose
                            and not has_yellow
                            and not has_hydrangea
                            and not has_chrysanthemum
                            and not has_phlox
                        ):
                            image_url = photo.get("urls", {}).get("regular")
                            logger.info(
                                "  ✓ Найдено: белые гвоздики "
                                "(проверено: не розы, не желтые, не гортензии)"
                            )
                            return image_url
                    elif required_color == "pink":
                        has_pink = "pink" in all_text
                        # НЕ должны быть розы, гортензии, хризантемы
                        if (
                            has_carnation
                            and has_pink
                            and not has_rose
                            and not has_hydrangea
                            and not has_chrysanthemum
                        ):
                            image_url = photo.get("urls", {}).get("regular")
                            logger.info(
                                "  ✓ Найдено: розовые гвоздики "
                                "(проверено: не розы, не гортензии)"
                            )
                            return image_url

                # Если не нашли идеальное, проверяем ВСЕ результаты более тщательно
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

                    # Строгая проверка: должны быть гвоздики, НЕ другие цветы
                    has_carnation = "carnation" in all_text or "dianthus" in all_text
                    has_rose = "rose" in all_text and "carnation" not in all_text
                    has_hydrangea = (
                        "hydrangea" in all_text or "гортензия" in all_text.lower()
                    )
                    has_chrysanthemum = (
                        "chrysanthemum" in all_text or "хризантема" in all_text.lower()
                    )
                    has_phlox = "phlox" in all_text or "флокс" in all_text.lower()
                    has_hibiscus = (
                        "hibiscus" in all_text or "гибискус" in all_text.lower()
                    )

                    # Проверка цвета
                    if required_color == "white":
                        has_white = "white" in all_text
                        has_yellow = "yellow" in all_text
                        if (
                            has_carnation
                            and has_white
                            and not has_rose
                            and not has_yellow
                            and not has_hydrangea
                            and not has_chrysanthemum
                            and not has_phlox
                            and not has_hibiscus
                        ):
                            image_url = photo.get("urls", {}).get("regular")
                            logger.info(
                                "  ✓ Найдено: белые гвоздики "
                                "(строгая проверка пройдена)"
                            )
                            return image_url
                    elif required_color == "pink":
                        has_pink = "pink" in all_text
                        if (
                            has_carnation
                            and has_pink
                            and not has_rose
                            and not has_hydrangea
                            and not has_chrysanthemum
                            and not has_phlox
                            and not has_hibiscus
                        ):
                            image_url = photo.get("urls", {}).get("regular")
                            logger.info(
                                "  ✓ Найдено: розовые гвоздики "
                                "(строгая проверка пройдена)"
                            )
                            return image_url

                # Если ничего не нашли - возвращаем None,
                # не берем неправильное изображение
                logger.warning(
                    f"  ⚠ Не найдено подходящего изображения гвоздик "
                    f"среди {len(data['results'])} результатов"
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
    logger.info("ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ КАРТИНОК 118, 119, 120, 121")
    logger.info("=" * 80)
    logger.info("118-119: БЕЛЫЕ ГВОЗДИКИ (не желтые, не розы)")
    logger.info("120-121: РОЗОВЫЕ ГВОЗДИКИ (не розы)")
    logger.info("")

    # Список букетов для исправления
    # Используем максимально специфичные запросы для правильных гвоздик
    flowers_to_fix = [
        {
            "name_part": "Белые гвоздики",
            "count": "25 шт",
            "queries": [
                "white carnation flower bouquet",
                "white dianthus caryophyllus",
                "white carnation close up",
                "white carnation single flower",
                "white carnation petals",
            ],
            "color": "white",
        },
        {
            "name_part": "Белые гвоздики",
            "count": "15 шт",
            "queries": [
                "white carnation flower bouquet",
                "white dianthus caryophyllus",
                "white carnation close up",
                "white carnation single flower",
                "white carnation petals",
            ],
            "color": "white",
        },
        {
            "name_part": "Розовые гвоздики",
            "count": "25 шт",
            "queries": [
                "pink carnation flower bouquet",
                "pink dianthus caryophyllus",
                "pink carnation close up",
                "pink carnation single flower",
                "pink carnation petals",
            ],
            "color": "pink",
        },
        {
            "name_part": "Розовые гвоздики",
            "count": "15 шт",
            "queries": [
                "pink carnation flower bouquet",
                "pink dianthus caryophyllus",
                "pink carnation close up",
                "pink carnation single flower",
                "pink carnation petals",
            ],
            "color": "pink",
        },
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

            image_url = None
            # Пробуем несколько запросов, пока не найдем правильное изображение
            for query in flower_info["queries"]:
                logger.info(f"  Поиск: '{query}'")
                image_url = get_unsplash_image(
                    query, UNSPLASH_ACCESS_KEY, required_color=flower_info["color"]
                )
                if image_url:
                    break  # Нашли подходящее изображение

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

                        # Небольшая задержка между запросами
                        time.sleep(0.5)
                    else:
                        logger.warning(
                            f"  ⚠ Не удалось скачать изображение: "
                            f"{img_response.status_code}"
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
        logger.info("✅ Картинки должны теперь показывать ПРАВИЛЬНЫЕ гвоздики!")
    logger.info("=" * 80)
