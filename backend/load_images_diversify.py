"""
Скрипт для разнообразия изображений букетов
Загружает разные изображения для каждого букета, даже если названия похожи
"""

import os
import re
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

# Unsplash API ключ
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def normalize_flower_name(name):
    """Нормализует название цветка"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    return clean


def get_diverse_search_query(flower_name, index=0):
    """Создает разнообразные поисковые запросы для одного и того же типа букета"""
    normalized = normalize_flower_name(flower_name)

    # Словарь переводов
    translations = {
        "розы": "roses",
        "альстромерии": "alstroemeria",
        "фрезии": "freesia",
        "тюльпаны": "tulips",
        "хризантемы": "chrysanthemums",
        "гвоздики": "carnations",
        "лилии": "lilies",
        "ирисы": "irises",
        "орхидеи": "orchids",
        "пионы": "peonies",
        "герберы": "gerberas",
        "эустомы": "eustoma",
        "белые": "white",
        "красные": "red",
        "розовые": "pink",
        "желтые": "yellow",
        "оранжевые": "orange",
        "фиолетовые": "purple",
        "синие": "blue",
        "смешанный": "mixed",
        "букет": "bouquet",
    }

    # Варианты поисковых запросов для разнообразия
    variations = [
        # Вариант 1: стандартный
        lambda n: f"{n} bouquet",
        # Вариант 2: с "fresh"
        lambda n: f"fresh {n} bouquet",
        # Вариант 3: с "beautiful"
        lambda n: f"beautiful {n} bouquet",
        # Вариант 4: с "elegant"
        lambda n: f"elegant {n} arrangement",
        # Вариант 5: с "luxury"
        lambda n: f"luxury {n} flowers",
        # Вариант 6: с "romantic"
        lambda n: f"romantic {n} bouquet",
        # Вариант 7: с "wedding"
        lambda n: f"wedding {n} arrangement",
        # Вариант 8: с "gift"
        lambda n: f"gift {n} bouquet",
        # Вариант 9: с "florist"
        lambda n: f"florist {n} arrangement",
        # Вариант 10: с "professional"
        lambda n: f"professional {n} bouquet",
    ]

    # Заменяем русские слова на английские
    result = normalized
    for ru, en in translations.items():
        result = result.replace(ru, en)

    # Выбираем вариант на основе индекса
    variation_func = variations[index % len(variations)]
    return variation_func(result)


def get_unsplash_image(search_query, api_key, skip_first=0):
    """
    Получает изображение из Unsplash API,
    пропуская первые N результатов для разнообразия
    """
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        params = {
            "query": search_query,
            "per_page": 10,  # Берем больше результатов для выбора
            "orientation": "landscape",
        }

        # Пробуем несколько раз с увеличивающимся таймаутом
        max_retries = 3
        for attempt in range(max_retries):
            try:
                timeout = 15 + (attempt * 5)
                response = requests.get(
                    UNSPLASH_API_URL, headers=headers, params=params, timeout=timeout
                )
                break
            except (
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
            ):
                if attempt < max_retries - 1:
                    logger.warning(
                        f"  ⚠ Таймаут (попытка {attempt + 1}/{max_retries}), "
                        f"повторяю через 2 секунды..."
                    )
                    time.sleep(2)
                else:
                    raise

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Пропускаем первые skip_first результатов для разнообразия
                available_photos = data["results"][skip_first:]
                if available_photos:
                    photo = available_photos[0]  # Берем первый из оставшихся
                    return photo.get("urls", {}).get("regular")
                else:
                    # Если пропустили все, берем последний
                    photo = data["results"][-1]
                    return photo.get("urls", {}).get("regular")
        elif response.status_code == 403:
            logger.error("✗ Ошибка 403: Превышен лимит запросов или нет прав доступа")
            return None
        else:
            logger.error(f"✗ Ошибка при запросе: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"✗ Ошибка при запросе: {e}")
        return None


def load_diverse_images():
    """Загружает разнообразные изображения для всех цветов"""
    flowers = Flower.objects.filter(in_stock=True).order_by("id")

    logger.info("=" * 80)
    logger.info("РАЗНООБРАЗИЕ ИЗОБРАЖЕНИЙ ДЛЯ БУКЕТОВ")
    logger.info("=" * 80)
    logger.info(f"Найдено цветов: {flowers.count()}")
    logger.info("")

    if not UNSPLASH_ACCESS_KEY:
        logger.error("❌ UNSPLASH_ACCESS_KEY не установлен!")
        return

    updated = 0
    skipped = 0
    errors = 0

    # Группируем цветы по нормализованному названию для разнообразия
    flower_groups = {}
    for flower in flowers:
        normalized = normalize_flower_name(flower.name)
        if normalized not in flower_groups:
            flower_groups[normalized] = []
        flower_groups[normalized].append(flower)

    logger.info(f"Найдено уникальных типов букетов: {len(flower_groups)}")
    logger.info("")

    for normalized_name, flower_list in flower_groups.items():
        logger.info(
            f"Обрабатываем группу: '{normalized_name}' ({len(flower_list)} вариантов)"
        )

        for idx, flower in enumerate(flower_list):
            # Для каждого цветка используем разный вариант запроса и пропускаем разные
            # результаты
            search_query = get_diverse_search_query(flower.name, idx)
            skip_count = idx  # Пропускаем первые idx результатов для разнообразия

            logger.info(
                f"  '{flower.name}' -> поиск: '{search_query}' (пропуск: {skip_count})"
            )

            image_url = get_unsplash_image(
                search_query, UNSPLASH_ACCESS_KEY, skip_first=skip_count
            )

            if image_url:
                try:
                    # Скачиваем изображение
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        # Генерируем уникальное имя файла
                        timestamp = int(time.time())
                        safe_name = (
                            re.sub(r"[^\w\s-]", "", flower.name)
                            .strip()
                            .replace(" ", "_")
                        )
                        filename = f"flowers/{safe_name}_{timestamp}.jpg"

                        # Сохраняем изображение
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
                    errors += 1
            else:
                logger.warning("  ⚠ Не удалось получить изображение")
                skipped += 1

        logger.info("")

    logger.info("=" * 80)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {errors}"
    )
    logger.info("=" * 80)


if __name__ == "__main__":
    load_diverse_images()
