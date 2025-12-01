"""Загрузка изображения для 'Розовые гвоздики (30 шт)' из файла с base64"""

import os
import re
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import base64
import logging

from django.core.files.base import ContentFile
from django.db.models import Q

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Читаем base64 из файла
base64_file = "pink_carnations_30_base64.txt"
if not os.path.exists(base64_file):
    logger.error(f"✗ Файл {base64_file} не найден!")
    sys.exit(1)

with open(base64_file, "r", encoding="utf-8") as f:
    base64_data = f.read().strip()

logger.info("=" * 80)
logger.info("ЗАГРУЗКА ИЗОБРАЖЕНИЯ ДЛЯ 'Розовые гвоздики (30 шт)' ИЗ ФАЙЛА")
logger.info("=" * 80)

# Декодируем base64
try:
    if base64_data.startswith("data:image"):
        header, encoded = base64_data.split(",", 1)
    else:
        encoded = base64_data

    # Добавляем padding если нужно
    missing_padding = len(encoded) % 4
    if missing_padding:
        encoded += "=" * (4 - missing_padding)

    image_data = base64.b64decode(encoded)
    logger.info("✓ Base64 декодирован успешно")
except Exception as e:
    logger.error(f"✗ Ошибка декодирования base64: {e}")
    sys.exit(1)

# Находим цветок
flower = Flower.objects.filter(
    Q(name__icontains="Розовые гвоздики") & Q(name__icontains="30 шт")
).first()

if not flower:
    logger.error("✗ Цветок 'Розовые гвоздики (30 шт)' не найден!")
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
import time

safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip().replace(" ", "_")
unique_filename = f"flowers/{safe_name}_{int(time.time())}.jpg"

flower.image.save(unique_filename, ContentFile(image_data), save=False)
flower.image_url = None
flower.save()

logger.info(f"  ✅ Изображение сохранено: {flower.image.name}")
logger.info("=" * 80)
logger.info("✅ ГОТОВО! Обнови страницу в браузере (Ctrl+F5)")
logger.info("=" * 80)
