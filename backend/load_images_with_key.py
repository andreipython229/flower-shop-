"""
Скрипт для загрузки изображений через Unsplash API с правильным использованием ключа
"""

import os
import re

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

# Получаем ключ из переменной окружения или используем дефолтный
UNSPLASH_ACCESS_KEY = os.environ.get(
    "UNSPLASH_ACCESS_KEY", "YIjTAjb14kWataGu6LAbCvgheBU1r7pM1R0u98tR9nQ"
).strip()
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def get_unsplash_image(search_query):
    """Получает изображение из Unsplash API"""
    try:
        params = {
            "query": search_query,
            "per_page": 1,
            "client_id": UNSPLASH_ACCESS_KEY,  # Правильное имя параметра для Unsplash
        }

        response = requests.get(UNSPLASH_API_URL, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                image_url = data["results"][0]["urls"]["regular"]
                return image_url
        elif response.status_code == 401:
            logger.error("✗ ОШИБКА: Недействительный API ключ! Статус 401")
            logger.error(f"  Ключ: {UNSPLASH_ACCESS_KEY[:20]}...")
            logger.error(
                "  Нужно получить новый ключ на https://unsplash.com/developers"
            )
            return None
        else:
            status_code = response.status_code
            response_text = response.text[:200]
            logger.warning(
                f"⚠ Unsplash API вернул статус {status_code}: {response_text}"
            )
            return None

    except Exception as e:
        logger.error(f"Ошибка при запросе к Unsplash API: {e}")
        return None


def get_search_query(flower_name):
    """Преобразует русское название в английский поисковый запрос"""
    normalized = re.sub(r"\s*\(\d+\s*шт\)", "", flower_name.lower()).strip()

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
    flower_map = {
        "розы": "roses",
        "гвоздики": "carnations",
        "герберы": "gerbera",
        "ромашки": "daisies",
        "тюльпаны": "tulips",
        "хризантемы": "chrysanthemums",
        "пионы": "peonies",
        "лилии": "lilies",
        "ирисы": "irises",
        "орхидеи": "orchids",
        "альстромерии": "alstroemeria",
        "фрезии": "freesia",
        "астры": "asters",
        "гладиолусы": "gladiolus",
        "эустомы": "eustoma",
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

    if found_color and found_flower:
        return f"{found_color} {found_flower} bouquet"
    elif found_flower:
        return f"{found_flower} bouquet"
    else:
        return "flower bouquet"


def load_images():
    """Загружает изображения для всех цветов"""
    flowers = Flower.objects.all()

    logger.info(f"Начинаем загрузку изображений для {flowers.count()} цветов...")
    logger.info(f"Используем Unsplash API с ключом: {UNSPLASH_ACCESS_KEY[:20]}...")

    # Сначала тестируем ключ
    logger.info("Тестируем API ключ...")
    test_url = get_unsplash_image("red roses")
    if not test_url:
        logger.error("✗ API ключ не работает! Статус 401 - ключ невалиден.")
        logger.error("Получите новый ключ на https://unsplash.com/developers")
        logger.error("Затем установите его: set UNSPLASH_ACCESS_KEY=ваш_новый_ключ")
        logger.error("")
        logger.error("АЛЬТЕРНАТИВА: Используйте скрипт load_images_smart.py")
        logger.error(
            "Он автоматически переключится на локальные изображения, "
            "если ключ не работает."
        )
        return
    else:
        logger.info(f"✓ API ключ работает! Тестовый URL: {test_url[:50]}...")

    updated = 0
    failed = 0
    skipped = 0

    for flower in flowers:
        try:
            search_query = get_search_query(flower.name)
            image_url = get_unsplash_image(search_query)

            if not image_url:
                logger.warning(
                    f"⚠ Не найдено изображение для '{flower.name}' "
                    f"(запрос: '{search_query}')"
                )
                skipped += 1
                continue

            # Скачиваем и сохраняем
            try:
                response = requests.get(
                    image_url,
                    stream=True,
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                response.raise_for_status()

                # Удаляем старое
                if flower.image:
                    try:
                        old_path = flower.image.path
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception:
                        pass

                # Сохраняем новое
                safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                safe_name = re.sub(r"[-\s]+", "_", safe_name)
                file_name = f"{safe_name}.jpg"

                image_content = ContentFile(response.content)
                image_path = default_storage.save(f"flowers/{file_name}", image_content)

                flower.image = image_path
                flower.image_url = None
                flower.save()

                logger.info(f"✓ '{flower.name}' -> {search_query}")
                updated += 1

            except Exception as e:
                logger.warning(f"⚠ Ошибка при скачивании для '{flower.name}': {e}")
                failed += 1

        except Exception as e:
            logger.error(f"✗ Ошибка для '{flower.name}': {e}")
            failed += 1

    logger.info("\n" + "=" * 60)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {failed}"
    )


if __name__ == "__main__":
    load_images()
