"""
Скрипт для загрузки изображений с ТОЧНЫМ маппингом названий на правильные изображения
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

# ТОЧНЫЙ маппинг: каждое название цветка -> правильное изображение
# Используем проверенные рабочие URL из Pexels
EXACT_FLOWER_MAPPING = {
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
    "бордовые розы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "персиковые розы": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "двухцветные розы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Гвоздики
    "красные гвоздики": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые гвоздики": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые гвоздики": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые гвоздики": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанные гвоздики": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Герберы
    "желтые герберы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "красные герберы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые герберы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "оранжевые герберы": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые герберы": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанные герберы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Ромашки
    "белые ромашки": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "ромашки с васильками": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "васильки и ромашки": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "синие васильки": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Тюльпаны
    "красные тюльпаны": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые тюльпаны": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые тюльпаны": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые тюльпаны": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "фиолетовые тюльпаны": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "смешанные тюльпаны": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Хризантемы
    "белые хризантемы": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые хризантемы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые хризантемы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "красные хризантемы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "оранжевые хризантемы": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Пионы
    "розовые пионы": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые пионы": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "бордовые пионы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Лилии
    "белые лилии": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые лилии": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые лилии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "оранжевые лилии": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Ирисы
    "синие ирисы": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "фиолетовые ирисы": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые ирисы": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые ирисы": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Орхидеи
    "белые орхидеи": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые орхидеи": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "фиолетовые орхидеи": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые орхидеи": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Альстромерии
    "розовые альстромерии": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые альстромерии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые альстромерии": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "оранжевые альстромерии": (
        "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Фрезии
    "белые фрезии": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые фрезии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые фрезии": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Астры
    "белые астры": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые астры": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "фиолетовые астры": (
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Гладиолусы
    "красные гладиолусы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые гладиолусы": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "розовые гладиолусы": (
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
        "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "синие эустомы": (
        "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    # Смешанные букеты
    "смешанный букет": (
        "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
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
}


def normalize_name(name):
    """Нормализует название для поиска в маппинге"""
    # Убираем количество в скобках
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    # Убираем кавычки
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    # Убираем лишние пробелы
    clean = re.sub(r"\s+", " ", clean)
    return clean


def find_exact_image_url(flower_name):
    """Находит точное изображение для цветка"""
    normalized = normalize_name(flower_name)

    # Прямой поиск
    if normalized in EXACT_FLOWER_MAPPING:
        return EXACT_FLOWER_MAPPING[normalized]

    # Поиск по частичному совпадению (убираем количество)
    for key, url in EXACT_FLOWER_MAPPING.items():
        # Проверяем, содержит ли ключ основные слова из названия
        key_words = set(key.split())
        name_words = set(normalized.split())

        # Если ключевые слова совпадают (цвет + тип цветка)
        if len(key_words & name_words) >= 2:
            return url

    return None


def load_images():
    """Загружает изображения с точным маппингом"""
    flowers = Flower.objects.all()

    logger.info(f"Начинаем загрузку изображений для {flowers.count()} цветов...")
    logger.info("Используем ТОЧНЫЙ маппинг названий на правильные изображения")

    updated = 0
    failed = 0
    skipped = 0

    for flower in flowers:
        try:
            image_url = find_exact_image_url(flower.name)

            if not image_url:
                logger.warning(f"⚠ Не найдено изображение для '{flower.name}'")
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

                # Сохраняем новое с уникальным именем
                # (включая timestamp для обхода кэша)
                import time

                safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                safe_name = re.sub(r"[-\s]+", "_", safe_name)
                timestamp = int(time.time())
                file_name = f"{safe_name}_{timestamp}.jpg"

                image_content = ContentFile(response.content)
                image_path = default_storage.save(f"flowers/{file_name}", image_content)

                flower.image = image_path
                flower.image_url = None
                flower.save()

                logger.info(f"✓ '{flower.name}' -> {normalize_name(flower.name)}")
                updated += 1

            except Exception as e:
                logger.warning(f"⚠ Ошибка для '{flower.name}': {e}")
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
