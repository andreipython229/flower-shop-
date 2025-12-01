"""
Скрипт для загрузки изображений через Pexels API с точным поиском
Требует бесплатный API ключ от Pexels (получить на https://www.pexels.com/api/)
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

# Pexels API ключ (получить бесплатно на https://www.pexels.com/api/)
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "").strip()
PEXELS_API_URL = "https://api.pexels.com/v1/search"


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
        # Для конкретных цветов используем более специфичные запросы
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


def get_pexels_image(search_query, api_key):
    """Получает изображение из Pexels API"""
    if not api_key:
        logger.warning("⚠ Pexels API ключ не установлен!")
        logger.warning("Получите бесплатный ключ на https://www.pexels.com/api/")
        logger.warning("Затем установите: set PEXELS_API_KEY=ваш_ключ")
        return None

    try:
        headers = {"Authorization": api_key}

        params = {"query": search_query, "per_page": 1, "orientation": "portrait"}

        response = requests.get(
            PEXELS_API_URL, headers=headers, params=params, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("photos") and len(data["photos"]) > 0:
                # Берем лучшее качество
                photo = data["photos"][0]
                image_url = photo.get("src", {}).get("large") or photo.get(
                    "src", {}
                ).get("medium")
                logger.info(
                    f"  ✓ Найдено изображение: {photo.get('photographer', 'Unknown')}"
                )
                return image_url
            else:
                logger.warning(f"  ⚠ Нет результатов для запроса: '{search_query}'")
                return None
        elif response.status_code == 401:
            logger.error("✗ Pexels API ключ невалиден (401)")
            logger.error("Проверьте правильность ключа")
            return None
        else:
            logger.warning(f"⚠ Pexels API вернул статус {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"✗ Ошибка при запросе к Pexels API: {e}")
        return None


def load_images():
    """Загружает изображения для всех цветов через Pexels API"""
    flowers = Flower.objects.all()

    logger.info("=" * 80)
    logger.info("ЗАГРУЗКА ИЗОБРАЖЕНИЙ ЧЕРЕЗ PEXELS API")
    logger.info("=" * 80)

    # Проверяем наличие ключа
    if not PEXELS_API_KEY:
        logger.error("❌ PEXELS_API_KEY не установлен!")
        logger.error("")
        logger.error("ИНСТРУКЦИЯ:")
        logger.error("1. Зарегистрируйся на https://www.pexels.com/api/")
        logger.error("2. Создай приложение и получи API ключ")
        logger.error("3. Установи ключ: set PEXELS_API_KEY=твой_ключ")
        logger.error("")
        return

    logger.info(f"✓ API ключ найден: {PEXELS_API_KEY[:20]}...")
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
            image_url = get_pexels_image(search_query, PEXELS_API_KEY)

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
