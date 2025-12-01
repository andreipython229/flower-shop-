"""
Скрипт для исправления изображений цветов с использованием Unsplash API
"""

import logging
import os
import re

import django
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Unsplash API (используем Source API - не требует ключа)
UNSPLASH_SOURCE_API = "https://source.unsplash.com/600x600/?"


def normalize_flower_name(name):
    """Нормализует название цветка для поиска"""
    clean_name = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean_name = re.sub(r"\s+", " ", clean_name)
    return clean_name


def get_search_query(flower_name):
    """Преобразует русское название в английский поисковый запрос"""
    normalized = normalize_flower_name(flower_name)

    # Цвета
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

    # Типы цветов
    flower_map = {
        "розы": "roses",
        "гвоздики": "carnations",
        "герберы": "gerbera",
        "ромашки": "daisies",
        "васильки": "cornflowers",
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

    # Формируем поисковый запрос
    if found_color and found_flower:
        return f"{found_color} {found_flower} bouquet"
    elif found_flower:
        return f"{found_flower} bouquet"
    elif "смешанный букет" in normalized or "букет" in normalized:
        return "flower bouquet"
    else:
        return "flowers"


def get_unsplash_image_url(search_query):
    """Получает URL изображения из Unsplash Source API"""
    try:
        # Unsplash Source API возвращает случайное изображение по запросу
        # Используем размер 600x600 для оптимизации
        url = f"{UNSPLASH_SOURCE_API}{search_query.replace(' ', ',')}"

        # Делаем HEAD запрос для получения финального URL
        response = requests.head(url, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            final_url = response.url
            logger.info(f"✓ Получен URL из Unsplash: {final_url}")
            return final_url
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении URL из Unsplash: {e}")
        return None


def fix_flower_images():
    """Исправляет изображения для всех цветов используя Unsplash"""
    flowers = Flower.objects.all()

    logger.info(f"Начинаем исправление изображений для {flowers.count()} цветов...")
    logger.info("Используем Unsplash Source API для получения правильных изображений")

    updated = 0
    failed = 0
    skipped = 0

    for flower in flowers:
        try:
            # Получаем поисковый запрос
            search_query = get_search_query(flower.name)
            logger.info(f"\nОбработка: '{flower.name}' -> '{search_query}'")

            # Получаем URL изображения из Unsplash
            image_url = get_unsplash_image_url(search_query)

            if not image_url:
                logger.warning(
                    f"⚠ Не удалось получить изображение для '{
        flower.name}'. Пропускаем."
                )
                skipped += 1
                continue

            # Удаляем старое изображение, если оно есть
            if flower.image:
                try:
                    old_image_path = flower.image.path
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                        logger.info("  Удалено старое изображение")
                except Exception as e:
                    logger.warning(f"  Не удалось удалить старое изображение: {e}")

            # Скачиваем новое изображение
            try:
                response = requests.get(
                    image_url,
                    stream=True,
                    timeout=15,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )
                response.raise_for_status()

                # Создаем безопасное имя файла
                safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                safe_name = re.sub(r"[-\s]+", "_", safe_name)

                # Определяем расширение из Content-Type или URL
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

                # Обновляем запись цветка
                flower.image = image_path
                flower.image_url = None
                flower.save()

                logger.info(f"✓ Обновлено изображение для '{flower.name}'")
                updated += 1

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"⚠ Не удалось скачать изображение для '{flower.name}': {e}"
                )
                failed += 1
            except Exception as e:
                logger.warning(
                    f"⚠ Ошибка при сохранении файла для '{flower.name}': {e}"
                )
                failed += 1

        except Exception as e:
            logger.error(f"✗ Ошибка при обработке цветка '{flower.name}': {e}")
            failed += 1
            continue

    logger.info("\n" + "=" * 60)
    logger.info("Исправление завершено!")
    logger.info(f"Обновлено: {updated}")
    logger.info(f"Пропущено: {skipped}")
    logger.info(f"Ошибок: {failed}")
    logger.info(f"Всего: {flowers.count()}")


if __name__ == "__main__":
    fix_flower_images()
