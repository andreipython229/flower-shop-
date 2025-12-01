"""
Скрипт для исправления изображений цветов с правильным маппингом по названиям
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

# Правильный маппинг русских названий цветов на URL изображений из Pexels
FLOWER_IMAGES_MAP = {
    # Розы
    "красные розы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые розы": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые розы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые розы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "оранжевые розы": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "персиковые розы": (
        "https://images.pexels.com/photos/2072168/pexels-photo-2072168.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "бордовые розы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Гвоздики
    "красные гвоздики": (
        "https://images.pexels.com/photos/169191/pexels-photo-169191.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые гвоздики": (
        "https://images.pexels.com/photos/1793525/pexels-photo-1793525.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые гвоздики": (
        "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые гвоздики": (
        "https://images.pexels.com/photos/2072168/pexels-photo-2072168.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Герберы
    "желтые герберы": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "красные герберы": (
        "https://images.pexels.com/photos/2300714/pexels-photo-2300714.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые герберы": (
        "https://images.pexels.com/photos/2300715/pexels-photo-2300715.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "оранжевые герберы": (
        "https://images.pexels.com/photos/2300716/pexels-photo-2300716.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые герберы": (
        "https://images.pexels.com/photos/2300717/pexels-photo-2300717.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Ромашки
    "белые ромашки": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Тюльпаны
    "красные тюльпаны": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые тюльпаны": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые тюльпаны": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые тюльпаны": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Хризантемы
    "белые хризантемы": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые хризантемы": (
        "https://images.pexels.com/photos/169191/pexels-photo-169191.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые хризантемы": (
        "https://images.pexels.com/photos/1793525/pexels-photo-1793525.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "красные хризантемы": (
        "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "оранжевые хризантемы": (
        "https://images.pexels.com/photos/2072168/pexels-photo-2072168.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Пионы
    "розовые пионы": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые пионы": (
        "https://images.pexels.com/photos/2300714/pexels-photo-2300714.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "бордовые пионы": (
        "https://images.pexels.com/photos/2300715/pexels-photo-2300715.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Лилии
    "белые лилии": (
        "https://images.pexels.com/photos/2300716/pexels-photo-2300716.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые лилии": (
        "https://images.pexels.com/photos/2300717/pexels-photo-2300717.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые лилии": (
        "https://images.pexels.com/photos/2300719/pexels-photo-2300719.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "оранжевые лилии": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Альстромерии
    "розовые альстромерии": (
        "https://images.pexels.com/photos/169191/pexels-photo-169191.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые альстромерии": (
        "https://images.pexels.com/photos/1793525/pexels-photo-1793525.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "оранжевые альстромерии": (
        "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые альстромерии": (
        "https://images.pexels.com/photos/2072168/pexels-photo-2072168.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Фрезии
    "белые фрезии": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые фрезии": (
        "https://images.pexels.com/photos/2300714/pexels-photo-2300714.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые фрезии": (
        "https://images.pexels.com/photos/2300715/pexels-photo-2300715.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Астры
    "белые астры": (
        "https://images.pexels.com/photos/2300716/pexels-photo-2300716.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые астры": (
        "https://images.pexels.com/photos/2300717/pexels-photo-2300717.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "фиолетовые астры": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Орхидеи
    "белые орхидеи": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые орхидеи": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "фиолетовые орхидеи": (
        "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые орхидеи": (
        "https://images.pexels.com/photos/2072168/pexels-photo-2072168.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Ирисы
    "синие ирисы": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "фиолетовые ирисы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые ирисы": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые ирисы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Эустомы
    "белые эустомы": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые эустомы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "фиолетовые эустомы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "синие эустомы": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Гладиолусы
    "красные гладиолусы": (
        "https://images.pexels.com/photos/2300719/pexels-photo-2300719.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые гладиолусы": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые гладиолусы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Тюльпаны (дополнительные)
    "фиолетовые тюльпаны": (
        "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанные тюльпаны": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Васильки и ромашки
    "синие васильки": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "ромашки с васильками": (
        "https://images.pexels.com/photos/2300719/pexels-photo-2300719.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "васильки и ромашки": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Смешанные букеты
    "смешанный букет": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанный букет романтика": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанный букет полевой": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанный букет весенний": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанный букет летний": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанный букет осенний": (
        "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "свадебный букет": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "букет невесты": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанный букет премиум": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанный букет классика": (
        "https://images.pexels.com/photos/2300714/pexels-photo-2300714.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанный букет эксклюзив": (
        "https://images.pexels.com/photos/2300715/pexels-photo-2300715.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Дополнительные
    "двухцветные розы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанные герберы": (
        "https://images.pexels.com/photos/2300716/pexels-photo-2300716.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанные гвоздики": (
        "https://images.pexels.com/photos/1793525/pexels-photo-1793525.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
}


def normalize_flower_name(name):
    """Нормализует название цветка для поиска в маппинге"""
    # Убираем количество в скобках и приводим к нижнему регистру
    clean_name = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    # Убираем лишние пробелы
    clean_name = re.sub(r"\s+", " ", clean_name)
    return clean_name


def find_image_url(flower_name):
    """Находит URL изображения для цветка по его названию"""
    normalized_name = normalize_flower_name(flower_name)

    # Прямой поиск в маппинге
    if normalized_name in FLOWER_IMAGES_MAP:
        return FLOWER_IMAGES_MAP[normalized_name]

    # Поиск по частичному совпадению (например, "белые розы" в "белые розы (35 шт)")
    for key, url in FLOWER_IMAGES_MAP.items():
        if key in normalized_name or normalized_name in key:
            return url

    # Если не нашли, возвращаем None (будет использован placeholder)
    return None


def fix_flower_images():
    """Исправляет изображения для всех цветов"""
    flowers = Flower.objects.all()

    logger.info(f"Начинаем исправление изображений для {flowers.count()} цветов...")

    updated = 0
    failed = 0
    skipped = 0

    for flower in flowers:
        try:
            # Находим правильный URL изображения
            image_url = find_image_url(flower.name)

            if not image_url:
                logger.warning(
                    f"⚠ Изображение не найдено для '{flower.name}'. "
                    f"Будет использован placeholder."
                )
                skipped += 1
                continue

            # Удаляем старое изображение, если оно есть
            if flower.image:
                try:
                    old_image_path = flower.image.path
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                        logger.info(f"  Удалено старое изображение: {old_image_path}")
                except Exception as e:
                    logger.warning(f"  Не удалось удалить старое изображение: {e}")

            # Скачиваем новое изображение
            try:
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

                # Создаем безопасное имя файла
                safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                safe_name = re.sub(r"[-\s]+", "_", safe_name)
                file_extension = "jpg"
                if ".jpeg" in image_url or ".jpg" in image_url:
                    file_extension = "jpg"
                elif ".png" in image_url:
                    file_extension = "png"

                file_name = f"{safe_name}.{file_extension}"

                image_content = ContentFile(response.content)
                image_path = default_storage.save(f"flowers/{file_name}", image_content)

                # Обновляем запись цветка
                flower.image = image_path
                flower.image_url = (
                    None  # Очищаем image_url, используем только локальные файлы
                )
                flower.save()

                logger.info(
                    f"✓ Обновлено изображение для '{flower.name}' -> "
                    f"{normalize_flower_name(flower.name)}"
                )
                updated += 1

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"⚠ Не удалось скачать изображение {image_url} "
                    f"для '{flower.name}': {e}"
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

    logger.info("=" * 60)
    logger.info("Исправление завершено!")
    logger.info(f"Обновлено: {updated}")
    logger.info(f"Пропущено (нет маппинга): {skipped}")
    logger.info(f"Ошибок: {failed}")
    logger.info(f"Всего: {flowers.count()}")


if __name__ == "__main__":
    fix_flower_images()
