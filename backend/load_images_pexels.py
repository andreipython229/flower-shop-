"""
Скрипт для загрузки изображений через Pexels API
(бесплатный, не требует ключа для базового использования)
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

# Pexels API (можно использовать без ключа для ограниченного количества запросов)
# Или получить бесплатный ключ на pexels.com/api
PEXELS_API_KEY = os.environ.get(
    "PEXELS_API_KEY", ""
)  # Можно оставить пустым для базового использования
PEXELS_API_URL = "https://api.pexels.com/v1/search"


def get_pexels_image(search_query):
    """Получает изображение из Pexels API"""
    try:
        headers = {}
        if PEXELS_API_KEY:
            headers["Authorization"] = PEXELS_API_KEY
        else:
            # Без ключа используем базовый доступ (ограниченный)
            headers["User-Agent"] = "Mozilla/5.0"

        params = {"query": search_query, "per_page": 1, "orientation": "portrait"}

        response = requests.get(
            PEXELS_API_URL, headers=headers, params=params, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("photos") and len(data["photos"]) > 0:
                image_url = data["photos"][0]["src"]["large"]
                return image_url
        elif response.status_code == 401:
            logger.warning(
                "⚠ Pexels API требует ключ. Получите бесплатный ключ на pexels.com/api"
            )
            return None
        else:
            logger.warning(f"⚠ Pexels API вернул статус {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Ошибка при запросе к Pexels API: {e}")
        return None


def load_images():
    """Загружает изображения для всех цветов"""
    flowers = Flower.objects.all()

    logger.info(f"Начинаем загрузку изображений для {flowers.count()} цветов...")
    logger.info("Используем Pexels API")

    # Маппинг русских названий на английские запросы
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

    updated = 0
    failed = 0
    skipped = 0

    for flower in flowers:
        try:
            # Формируем поисковый запрос
            normalized = re.sub(r"\s*\(\d+\s*шт\)", "", flower.name.lower()).strip()

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
                search_query = f"{found_color} {found_flower} bouquet"
            elif found_flower:
                search_query = f"{found_flower} bouquet"
            else:
                search_query = "flower bouquet"

            # Получаем изображение
            image_url = get_pexels_image(search_query)

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
        f"Загрузка завершена! Обновлено: {updated}, "
        f"Пропущено: {skipped}, Ошибок: {failed}"
    )


if __name__ == "__main__":
    load_images()
