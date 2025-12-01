"""
Скрипт для загрузки изображений через прямые URL Unsplash CDN
(без API ключа, как с собачками)
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

# Прямые URL изображений цветов из Unsplash CDN (не требуют API ключа)
FLOWER_IMAGES_DIRECT = {
    # Розы
    "красные розы": (
        "https://images.unsplash.com/photo-1518895949257-7621c3c786d7" "?w=600"
    ),
    "белые розы": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "розовые розы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "желтые розы": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    "оранжевые розы": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    # Гвоздики
    "красные гвоздики": (
        "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a" "?w=600"
    ),
    "розовые гвоздики": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    "белые гвоздики": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "желтые гвоздики": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    # Герберы
    "желтые герберы": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    "красные герберы": (
        "https://images.unsplash.com/photo-1518895949257-7621c3c786d7" "?w=600"
    ),
    "розовые герберы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "оранжевые герберы": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    "белые герберы": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    # Ромашки
    "белые ромашки": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    # Тюльпаны
    "красные тюльпаны": (
        "https://images.unsplash.com/photo-1518895949257-7621c3c786d7" "?w=600"
    ),
    "желтые тюльпаны": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    "розовые тюльпаны": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "белые тюльпаны": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    # Хризантемы
    "белые хризантемы": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "желтые хризантемы": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    "розовые хризантемы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "красные хризантемы": (
        "https://images.unsplash.com/photo-1518895949257-7621c3c786d7" "?w=600"
    ),
    # Пионы
    "розовые пионы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "белые пионы": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    # Лилии
    "белые лилии": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "розовые лилии": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    # Ирисы
    "синие ирисы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "фиолетовые ирисы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    # Орхидеи
    "белые орхидеи": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "розовые орхидеи": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "фиолетовые орхидеи": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "желтые орхидеи": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    # Альстромерии
    "розовые альстромерии": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "желтые альстромерии": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    "белые альстромерии": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "оранжевые альстромерии": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    # Фрезии
    "белые фрезии": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "желтые фрезии": (
        "https://images.unsplash.com/photo-1606041008020-472df57c2b1b" "?w=600"
    ),
    "розовые фрезии": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    # Астры
    "белые астры": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "розовые астры": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "фиолетовые астры": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    # Гладиолусы
    "красные гладиолусы": (
        "https://images.unsplash.com/photo-1518895949257-7621c3c786d7" "?w=600"
    ),
    "белые гладиолусы": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "розовые гладиолусы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    # Эустомы
    "белые эустомы": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "розовые эустомы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "фиолетовые эустомы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "синие эустомы": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    # Смешанные букеты
    "смешанный букет": (
        "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4" "?w=600"
    ),
    "свадебный букет": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
    "букет невесты": (
        "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11" "?w=600"
    ),
}


def normalize_name(name):
    """Нормализует название для поиска"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    return clean


def find_image_url(flower_name):
    """Находит URL изображения для цветка"""
    normalized = normalize_name(flower_name)

    # Прямой поиск
    if normalized in FLOWER_IMAGES_DIRECT:
        return FLOWER_IMAGES_DIRECT[normalized]

    # Поиск по частичному совпадению
    for key, url in FLOWER_IMAGES_DIRECT.items():
        if key in normalized or normalized in key:
            return url

    return None


def load_images():
    """Загружает изображения для всех цветов"""
    flowers = Flower.objects.all()

    logger.info(f"Начинаем загрузку изображений для {flowers.count()} цветов...")
    logger.info("Используем прямые URL из Unsplash CDN (без API ключа)")

    updated = 0
    failed = 0
    skipped = 0

    for flower in flowers:
        try:
            image_url = find_image_url(flower.name)

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

                # Сохраняем новое
                safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                safe_name = re.sub(r"[-\s]+", "_", safe_name)
                file_name = f"{safe_name}.jpg"

                image_content = ContentFile(response.content)
                image_path = default_storage.save(f"flowers/{file_name}", image_content)

                flower.image = image_path
                flower.image_url = None
                flower.save()

                logger.info(f"✓ '{flower.name}'")
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
