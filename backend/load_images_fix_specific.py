"""
Скрипт для исправления конкретных проблемных цветов через Unsplash API
Обновляет только указанные цветы
"""

import os
import re
import sys
import time

import django
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Unsplash API ключ
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Конкретные ID букетов, которые нужно исправить (найдены через find_mixed_bouquets.py)
# Это букеты на позициях 51-62 на фронтенде, которые показывают одинаковые изображения
FLOWERS_TO_FIX_IDS = [
    10867,  # Смешанный букет "Эксклюзив"
    10866,  # Смешанный букет "Классика"
    10865,  # Смешанный букет "Премиум"
    10864,  # Букет невесты
    10863,  # Свадебный букет
    10862,  # Смешанный букет "Осенний"
    10861,  # Смешанный букет "Летний"
    10860,  # Смешанный букет "Весенний"
    10859,  # Смешанный букет "Полевой" (большой)
    10858,  # Смешанный букет "Полевой" (средний)
    10857,  # Смешанный букет "Романтика" (большой)
    10856,  # Смешанный букет "Романтика" (средний)
]


def normalize_flower_name(name):
    """Нормализует название цветка"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    return clean


def get_english_search_query(flower_name, flower_id=None):
    """Преобразует русское название в английский поисковый запрос
    Для смешанных букетов создает уникальные запросы, чтобы получить разные изображения
    """
    normalized = normalize_flower_name(flower_name)

    # СПЕЦИАЛЬНЫЕ ЗАПРОСЫ ДЛЯ СМЕШАННЫХ БУКЕТОВ - каждый получает уникальный запрос
    # Это гарантирует, что каждый букет получит РАЗНОЕ изображение
    if "эксклюзив" in normalized:
        return "luxury premium mixed flower bouquet elegant arrangement"
    elif "классика" in normalized:
        return "classic traditional mixed flower bouquet white red"
    elif "премиум" in normalized:
        return "premium deluxe mixed flower arrangement colorful"
    elif "невесты" in normalized or "bride" in normalized.lower():
        return "bridal wedding bouquet white roses elegant"
    elif "свадебный" in normalized or "wedding" in normalized.lower():
        return "wedding bouquet elegant white pink roses flowers"
    elif "осенний" in normalized or "autumn" in normalized.lower():
        return "autumn fall mixed bouquet orange red yellow flowers"
    elif "романтика" in normalized or "romance" in normalized.lower():
        # Для большого и среднего используем разные варианты
        if "большой" in normalized or "large" in normalized.lower():
            return "romantic pink red rose mixed bouquet large"
        else:
            return "romantic pink red rose mixed bouquet medium"
    elif "летний" in normalized or "summer" in normalized.lower():
        return "summer bright colorful mixed flower bouquet vibrant"
    elif "весенний" in normalized or "spring" in normalized.lower():
        return "spring fresh pastel mixed flower bouquet pink yellow"
    elif "полевой" in normalized or "field" in normalized.lower():
        # Для большого и среднего используем разные варианты
        if "большой" in normalized or "large" in normalized.lower():
            return "wildflower field bouquet natural mixed flowers large"
        else:
            return "wildflower field bouquet natural mixed flowers medium"

    # Словарь переводов для остальных цветов
    translations = {
        "розы": "roses",
        "альстромерии": "alstroemeria",
        "фрезии": "freesia",
        "тюльпаны": "tulips",
        "хризантемы": "chrysanthemums",
        "гвоздики": "carnations",
        "лилии": "lilies",
        "ирисы": "irises",
        "белые": "white",
        "красные": "red",
        "розовые": "pink",
        "желтые": "yellow",
        "оранжевые": "orange",
        "фиолетовые": "purple",
        "синие": "blue",
    }

    # Специальные запросы для лучших результатов
    if "гвоздики" in normalized:
        color = (
            "pink"
            if "розовые" in normalized
            else (
                "red"
                if "красные" in normalized
                else (
                    "white"
                    if "белые" in normalized
                    else "yellow" if "желтые" in normalized else "pink"
                )
            )
        )
        return f"{color} carnation flowers bouquet"

    if "орхидеи" in normalized and "розовые" in normalized:
        return "pink phalaenopsis orchid bouquet"

    if "ирисы" in normalized and "фиолетовые" in normalized:
        return "purple iris flowers bouquet"

    if "орхидеи" in normalized and "фиолетовые" in normalized:
        return "purple phalaenopsis orchid bouquet"

    # Заменяем слова
    result = normalized
    for ru, en in translations.items():
        result = result.replace(ru, en)

    # Добавляем "bouquet" для лучших результатов
    if "bouquet" not in result:
        result = f"{result} bouquet"

    return result


def get_unsplash_image(search_query, api_key, skip_index=0):
    """Получает изображение из Unsplash API с улучшенным выбором
    skip_index - индекс результата, который нужно пропустить для разнообразия"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        params = {
            "query": search_query,
            "per_page": 10,  # Берем 10 результатов для разнообразия
            "orientation": "landscape",
        }

        # Пробуем несколько раз с увеличивающимся таймаутом
        max_retries = 3
        for attempt in range(max_retries):
            try:
                timeout = 15 + (attempt * 5)  # 15, 20, 25 секунд
                response = requests.get(
                    UNSPLASH_API_URL, headers=headers, params=params, timeout=timeout
                )
                break  # Успешно, выходим из цикла
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
                    raise  # Последняя попытка не удалась, пробрасываем исключение

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Пропускаем первые skip_index результатов для разнообразия
                available_photos = data["results"][skip_index:]

                if not available_photos:
                    # Если пропустили все, берем последний
                    available_photos = [data["results"][-1]]

                # Из оставшихся выбираем лучшее по релевантности
                query_words = set(search_query.lower().split())
                best_photo = None
                best_score = 0

                for photo in available_photos:
                    score = 0
                    # Проверяем описание
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

                    # Считаем совпадения ключевых слов
                    all_text = f"{description} {alt_description} {' '.join(tags)}"
                    for word in query_words:
                        if len(word) > 3:  # Игнорируем короткие слова
                            if word in all_text:
                                score += 2

                    # Бонус за точное совпадение цвета
                    color_words = [
                        "white",
                        "red",
                        "pink",
                        "yellow",
                        "blue",
                        "purple",
                        "orange",
                    ]
                    for color in color_words:
                        if color in search_query.lower() and color in all_text:
                            score += 5

                    # Штраф за неправильный цвет
                    # (если ищем розовые, но нашли фиолетовые)
                    if "pink" in search_query.lower() and "purple" in all_text:
                        score -= (
                            10  # Сильный штраф за фиолетовый цвет при поиске розового
                        )

                    # Штраф за неправильный цвет
                    # (если ищем фиолетовые, но нашли белые/синие)
                    if "purple" in search_query.lower():
                        if "white" in all_text or "blue" in all_text:
                            # Если в описании есть "white" или "blue",
                            # но нет "purple", снижаем score
                            if "purple" not in all_text and (
                                "white" in all_text or "blue" in all_text
                            ):
                                # Штраф за белый/синий цвет при поиске фиолетового
                                score -= 8

                        # Дополнительный штраф для орхидей:
                        # если ищем фиолетовые, но нашли белые
                        if (
                            "orchid" in search_query.lower()
                            and "white" in all_text
                            and "purple" not in all_text
                        ):
                            # Сильный штраф за белую орхидею при поиске фиолетовой
                            score -= 10

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                # Используем лучшее изображение или первое из доступных
                if best_photo:
                    photo = best_photo
                    image_url = photo.get("urls", {}).get("regular") or photo.get(
                        "urls", {}
                    ).get("small")
                    logger.info(
                        f"  ✓ Найдено изображение от "
                        f"{photo.get('user', {}).get('name', 'Unknown')} "
                        f"(score: {best_score}, пропущено: {skip_index})"
                    )
                    return image_url
                elif available_photos:
                    # Если не нашли лучшее, берем первое доступное
                    photo = available_photos[0]
                    image_url = photo.get("urls", {}).get("regular") or photo.get(
                        "urls", {}
                    ).get("small")
                    logger.info(
                        f"  ✓ Использовано первое доступное изображение "
                        f"(пропущено: {skip_index})"
                    )
                    return image_url
            else:
                logger.warning(f"  ⚠ Нет результатов для запроса: '{search_query}'")
                return None
        elif response.status_code == 403:
            logger.error("✗ 403 Forbidden - лимит исчерпан или нет прав")
            logger.error(
                "Проверь 'Read photos access' в настройках приложения Unsplash"
            )
            return None
        elif response.status_code == 401:
            logger.error("✗ Unsplash API ключ невалиден (401)")
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
        logger.error("Установите: $env:UNSPLASH_ACCESS_KEY='ваш_ключ'")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("ИСПРАВЛЕНИЕ КОНКРЕТНЫХ ЦВЕТОВ (51-62 позиции на фронтенде)")
    logger.info("=" * 80)

    # Находим цветы по ID
    flowers_to_update = Flower.objects.filter(id__in=FLOWERS_TO_FIX_IDS, in_stock=True)

    if not flowers_to_update.exists():
        logger.warning("⚠ Не найдено цветов для исправления!")
        sys.exit(0)

    logger.info(f"Найдено цветов для исправления: {flowers_to_update.count()}\n")

    updated = 0
    skipped = 0
    failed = 0

    # Создаем словарь для отслеживания индексов пропуска для каждого букета
    skip_indices = {}

    for idx, flower in enumerate(flowers_to_update):
        try:
            search_query = get_english_search_query(flower.name, flower.id)
            # Используем индекс букета для пропуска разных результатов
            # это гарантирует разные изображения
            skip_index = (
                idx * 2
            )  # Пропускаем 0, 2, 4, 6... результатов для разнообразия
            skip_indices[flower.id] = skip_index

            logger.info(
                f"'{flower.name}' (ID: {flower.id}) -> поиск: '{search_query}' "
                f"(пропуск: {skip_index})"
            )

            image_url = get_unsplash_image(
                search_query, UNSPLASH_ACCESS_KEY, skip_index=skip_index
            )

            if not image_url:
                logger.warning("  ⚠ Не удалось получить изображение")
                skipped += 1
                continue

            logger.info(f"  ✓ URL: {image_url[:80]}...")

            # Удаляем старое изображение
            if flower.image:
                try:
                    old_path = flower.image.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception:
                    pass

            # Скачиваем и сохраняем новое изображение
            try:
                response = requests.get(
                    image_url,
                    stream=True,
                    timeout=20,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36"
                        )
                    },
                )
                response.raise_for_status()

                safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                safe_name = re.sub(r"[-\s]+", "_", safe_name)
                timestamp = int(time.time())
                file_name = f"{safe_name}_{timestamp}.jpg"

                image_content = ContentFile(response.content)
                image_path = default_storage.save(f"flowers/{file_name}", image_content)

                flower.image = image_path
                flower.save()

                logger.info(f"  ✅ Изображение сохранено: {file_name}")
                updated += 1

                # Небольшая задержка, чтобы не перегружать API
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"  ✗ Ошибка при сохранении: {e}")
                failed += 1

        except Exception as e:
            logger.error(f"✗ Ошибка при обработке '{flower.name}': {e}")
            failed += 1

    logger.info("")
    logger.info("=" * 80)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {failed}"
    )
    logger.info("=" * 80)
