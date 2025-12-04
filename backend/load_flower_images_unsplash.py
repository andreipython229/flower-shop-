"""
Скрипт для загрузки изображений цветов через Unsplash API (как в проекте с собачками)
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging

from flowers.models import Flower
from flowers.parsers import FlowerParser

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_flower_images():
    """Загружает изображения для всех цветов через Unsplash API"""
    flowers = Flower.objects.all()
    parser = FlowerParser()

    logger.info(f"Начинаем загрузку изображений для {flowers.count()} цветов...")
    logger.info("Используем Unsplash API (как в проекте с собачками)")

    updated = 0
    failed = 0
    skipped = 0

    for flower in flowers:
        try:
            # Получаем search_query из названия цветка
            # Ищем в списке flower_types парсера
            search_query = None
            for flower_type in parser.flower_types:
                if flower_type["name"] == flower.name:
                    search_query = flower_type["search_query"]
                    break

            # Если не нашли в списке, формируем запрос из названия
            if not search_query:
                # Преобразуем русское название в английский запрос
                normalized = flower.name.lower()
                # Убираем количество в скобках
                normalized = (
                    normalized.replace("(", "")
                    .replace(")", "")
                    .replace("шт", "")
                    .strip()
                )

                # Простое преобразование
                color_map = {
                    "красные": "red",
                    "белые": "white",
                    "розовые": "pink",
                    "желтые": "yellow",
                    "синие": "blue",
                    "оранжевые": "orange",
                    "фиолетовые": "purple",
                    "бордовые": "burgundy",
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
                    search_query = f"{found_color} {found_flower} bouquet"
                elif found_flower:
                    search_query = f"{found_flower} bouquet"
                else:
                    search_query = "flower bouquet"

            # Используем метод парсера для получения изображения
            image_url = parser._get_working_image_url(flower.name, search_query)

            if not image_url:
                logger.warning(
                    f"⚠ Не найдено изображение для '{flower.name}' "
                    f"(запрос: '{search_query}')"
                )
                skipped += 1
                continue

            # Скачиваем и сохраняем изображение
            try:
                import re

                import requests
                from django.core.files.base import ContentFile
                from django.core.files.storage import default_storage

                response = requests.get(
                    image_url,
                    stream=True,
                    timeout=15,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36"
                        )
                    },
                )
                response.raise_for_status()

                # Удаляем старое изображение
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

                content_type = response.headers.get("Content-Type", "")
                if "jpeg" in content_type or "jpg" in content_type:
                    file_extension = "jpg"
                elif "png" in content_type:
                    file_extension = "png"
                else:
                    file_extension = "jpg"

                file_name = f"{safe_name}.{file_extension}"

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
    logger.info("Загрузка завершена!")
    logger.info(f"Обновлено: {updated}")
    logger.info(f"Пропущено: {skipped}")
    logger.info(f"Ошибок: {failed}")
    logger.info(f"Всего: {flowers.count()}")


if __name__ == "__main__":
    load_flower_images()
