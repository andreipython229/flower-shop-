"""Загружает изображение из файла bouquet.jpg для розовых гвоздик (25 шт)"""

import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging
import re
import time

from django.core.files.base import ContentFile

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

image_file = "bouquet.jpg"
if not os.path.exists(image_file):
    logger.error(f"✗ Файл {image_file} не найден!")
    sys.exit(1)

logger.info("=" * 80)
logger.info("ЗАГРУЗКА РОЗОВЫХ ГВОЗДИК (25 шт) ИЗ ФАЙЛА bouquet.jpg")
logger.info("=" * 80)

# Читаем файл
with open(image_file, "rb") as f:
    image_data = f.read()

logger.info(f"✓ Файл прочитан: {len(image_data)} байт")

# Находим цветок
flower = Flower.objects.filter(
    name__icontains="Розовые гвоздики", name__icontains="25 шт"
).first()

if not flower:
    logger.error("✗ Цветок 'Розовые гвоздики (25 шт)' не найден!")
    sys.exit(1)

logger.info(f"✓ Найден цветок: {flower.name} (ID: {flower.id})")

# Удаляем старое изображение
if flower.image:
    try:
        old_path = flower.image.path
        if os.path.exists(old_path):
            from django.core.files.storage import default_storage

            default_storage.delete(flower.image.name)
            logger.info(f"  🗑️ Старое изображение удалено: {flower.image.name}")
    except Exception as e:
        logger.warning(f"  ⚠ Не удалось удалить старое изображение: {e}")

# Сохраняем новое
safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip().replace(" ", "_")
unique_filename = f"flowers/{safe_name}_{int(time.time())}.jpg"

flower.image.save(unique_filename, ContentFile(image_data), save=False)
flower.image_url = None
flower.save()

logger.info(f"  ✅ Изображение сохранено: {flower.image.name}")
logger.info("=" * 80)
logger.info("✅ ГОТОВО! Обнови страницу в браузере (Ctrl+F5)")
logger.info("=" * 80)
