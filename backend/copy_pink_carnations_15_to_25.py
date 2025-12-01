"""Копирование изображения с 'Розовые гвоздики (15 шт)' на 'Розовые гвоздики (25 шт)'"""

import logging
import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(
        "КОПИРОВАНИЕ ИЗОБРАЖЕНИЯ С 'Розовые гвоздики (15 шт)' "
        "НА 'Розовые гвоздики (25 шт)'"
    )
    logger.info("=" * 80)

    # Находим источник (15 шт)
    source_flower = Flower.objects.filter(
        Q(name__icontains="Розовые гвоздики") & Q(name__icontains="15 шт")
    ).first()

    if not source_flower:
        logger.error("✗ Цветок 'Розовые гвоздики (15 шт)' не найден!")
        sys.exit(1)

    logger.info(f"✓ Источник найден: {source_flower.name} (ID: {source_flower.id})")

    if not source_flower.image:
        logger.error("✗ У источника нет изображения!")
        sys.exit(1)

    logger.info(f"  Изображение источника: {source_flower.image.name}")

    # Находим целевой цветок (25 шт)
    target_flower = Flower.objects.filter(
        Q(name__icontains="Розовые гвоздики") & Q(name__icontains="25 шт")
    ).first()

    if not target_flower:
        logger.error("✗ Цветок 'Розовые гвоздики (25 шт)' не найден!")
        sys.exit(1)

    logger.info(
        f"✓ Целевой цветок найден: {target_flower.name} (ID: {target_flower.id})"
    )

    # Удаляем старое изображение целевого цветка
    if target_flower.image:
        try:
            if os.path.exists(target_flower.image.path):
                default_storage.delete(target_flower.image.name)
                logger.info(
                    f"  🗑️ Старое изображение удалено: {target_flower.image.name}"
                )
        except Exception as e:
            logger.warning(f"  ⚠ Не удалось удалить старое изображение: {e}")

    # Копируем изображение
    try:
        # Читаем файл источника
        with open(source_flower.image.path, "rb") as f:
            image_data = f.read()

        # Генерируем уникальное имя файла для целевого цветка
        import re
        import time

        safe_flower_name = (
            re.sub(r"[^\w\s-]", "", target_flower.name).strip().replace(" ", "_")
        )
        unique_filename = f"flowers/{safe_flower_name}_{int(time.time())}.jpg"

        # Сохраняем новое изображение
        target_flower.image.save(unique_filename, ContentFile(image_data), save=False)
        target_flower.image_url = None
        target_flower.save()

        logger.info(
            f"  ✅ Изображение скопировано и сохранено: {target_flower.image.name}"
        )
        logger.info("=" * 80)
        logger.info("✅ ГОТОВО! Обнови страницу в браузере (Ctrl+F5)")
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"✗ Ошибка при копировании изображения: {e}")
        import traceback

        logger.error(traceback.format_exc())
        sys.exit(1)
