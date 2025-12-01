"""
Скрипт для загрузки изображений через Unsplash API с новым ключом
Требует валидный API ключ от Unsplash (получить на https://unsplash.com/developers)
"""

import os
import re
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

# Unsplash API ключ (получить на https://unsplash.com/developers)
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def normalize_flower_name(name):
    """Нормализует название цветка"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    clean = re.sub(r"\s+", " ", clean)
    return clean


def get_english_search_query(flower_name):
    """Преобразует русское название в точный английский поисковый запрос"""
    normalized = normalize_flower_name(flower_name)

    # Точный маппинг цветов
    color_map = {
        "красные": "red",
        "белые": "white",
        "розовые": "pink",
        "желтые": "yellow",
        "синие": "blue",
        "оранжевые": "orange",
        "фиолетовые": "purple",
        "бордовые": "burgundy",
        "персиковые": "peach",
    }

    # Точный маппинг типов цветов
    flower_map = {
        "розы": "roses",
        "гвоздики": "carnations",
        "герберы": "gerbera daisies",
        "ромашки": "daisies",
        "васильки": "cornflowers",
        "тюльпаны": "tulips",
        "хризантемы": "chrysanthemums",
        "пионы": "peonies",
        "лилии": "lilies",
        "ирисы": "irises",
        "орхидеи": "orchids",
        "альстромерии": "alstroemeria flowers",
        "фрезии": "freesia flowers",
        "астры": "asters",
        "гладиолусы": "gladiolus flowers",
        "эустомы": "eustoma flowers",
    }

    found_color = None
    found_flower = None

    for ru, en in color_map.items():
        if ru in normalized:
            found_color = en
            break

    for ru, en in flower_map.items():
        if ru in normalized:
            found_flower = en
            break

    # Формируем точный поисковый запрос
    if found_color and found_flower:
        if found_flower == "roses":
            return f"{found_color} {found_flower} bouquet"
        elif found_flower in [
            "freesia flowers",
            "alstroemeria flowers",
            "eustoma flowers",
        ]:
            return f"{found_color} {found_flower}"
        else:
            return f"{found_color} {found_flower} bouquet"
    elif found_flower:
        return f"{found_flower} bouquet"
    elif "смешанный букет" in normalized or "букет" in normalized:
        return "mixed flower bouquet"
    else:
        return "flowers"


def validate_unsplash_key(api_key):
    """Проверяет валидность Unsplash API ключа"""
    try:
        headers = {"Authorization": f"Client-ID {api_key}"}
        # Тестовый запрос
        test_url = "https://api.unsplash.com/search/photos"
        params = {"query": "roses", "per_page": 1}
        response = requests.get(test_url, headers=headers, params=params, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def get_unsplash_image(search_query, api_key):
    """Получает изображение из Unsplash API"""
    if not api_key:
        logger.warning("⚠ Unsplash API ключ не установлен!")
        return None

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        params = {
            "query": search_query,
            "per_page": 5,  # Берем 5 результатов для лучшего выбора
            "orientation": "landscape",
        }

        response = requests.get(
            UNSPLASH_API_URL, headers=headers, params=params, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Пробуем найти наиболее релевантное изображение
                # Проверяем описание и теги на наличие ключевых слов из запроса
                query_words = set(search_query.lower().split())
                best_photo = None
                best_score = 0

                for photo in data["results"]:
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

                    if score > best_score:
                        best_score = score
                        best_photo = photo

                # Используем лучшее изображение или первое, если не нашли
                photo = best_photo if best_photo else data["results"][0]
                image_url = photo.get("urls", {}).get("regular") or photo.get(
                    "urls", {}
                ).get("small")
                logger.info(
                    f"  ✓ Найдено изображение от {
        photo.get(
            'user',
            {}).get(
                'name',
                 'Unknown')} (score: {best_score})"
                )
                return image_url
            else:
                logger.warning(f"  ⚠ Нет результатов для запроса: '{search_query}'")
                return None
        elif response.status_code == 401:
            logger.error("✗ Unsplash API ключ невалиден (401)")
            logger.error("Получи новый ключ на https://unsplash.com/developers")
            return None
        else:
            logger.warning(f"⚠ Unsplash API вернул статус {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"✗ Ошибка при запросе к Unsplash API: {e}")
        return None


def load_images():
    """Загружает изображения для всех цветов через Unsplash API"""
    flowers = Flower.objects.all()

    logger.info("=" * 80)
    logger.info("ЗАГРУЗКА ИЗОБРАЖЕНИЙ ЧЕРЕЗ UNSPLASH API")
    logger.info("=" * 80)

    # Проверяем наличие ключа
    if not UNSPLASH_ACCESS_KEY:
        logger.error("❌ UNSPLASH_ACCESS_KEY не установлен!")
        logger.error("")
        logger.error("ИНСТРУКЦИЯ:")
        logger.error("1. Зарегистрируйся на https://unsplash.com/developers")
        logger.error("2. Создай приложение и получи Access Key")
        logger.error("3. Установи ключ: set UNSPLASH_ACCESS_KEY=твой_ключ")
        logger.error("")
        return

    # Проверяем валидность ключа
    logger.info(f"Проверяем API ключ: {UNSPLASH_ACCESS_KEY[:20]}...")
    if not validate_unsplash_key(UNSPLASH_ACCESS_KEY):
        logger.error(
            "✗ Ключ невалиден! Получи новый на https://unsplash.com/developers"
        )
        return

    logger.info("✓ API ключ валиден!")
    logger.info(f"\nНачинаем обработку {flowers.count()} цветов...\n")

    updated = 0
    skipped = 0
    failed = 0

    for flower in flowers:
        try:
            # Получаем точный поисковый запрос
            search_query = get_english_search_query(flower.name)
            logger.info(f"'{flower.name}' -> поиск: '{search_query}'")

            # Получаем URL изображения
            image_url = get_unsplash_image(search_query, UNSPLASH_ACCESS_KEY)

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
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
                flower.image_url = None
                flower.save()

                logger.info(f"  ✓ Сохранено: {file_name}")
                updated += 1

                # Небольшая задержка, чтобы не превысить лимит запросов
                time.sleep(0.3)

            except Exception as e:
                logger.warning(f"  ⚠ Ошибка при скачивании: {e}")
                failed += 1

        except Exception as e:
            logger.error(f"  ✗ Ошибка: {e}")
            failed += 1

    logger.info("\n" + "=" * 80)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {failed}"
    )
    logger.info("=" * 80)
    logger.info("\nВАЖНО: Проверь несколько изображений вручную в браузере!")
    logger.info(
        "Если они правильные - отлично! Если нет - нужно уточнить поисковые запросы."
    )
    logger.info("=" * 80)


if __name__ == "__main__":
    load_images()
